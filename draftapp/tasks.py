from draftapp.utility import consume_riot_api, transaction, localize_datetime, create_match, create_team, \
    create_summoner, create_participant, resolve_junglers, resolve_supports, resolve_top_lane, resolve_mid_lane, \
    inadequate_picks, binconf, adjust_win_rate, sort_dict, calc_rank_score, json, math, clean_pick_dictionary, \
    get_team_side, process_pick_data
from lib.utility_dicts import Lane_Dict
from loldraft.celery import app, rate_limit
from celery import chain
from draftapp.models import Summoner, Rank, Match, Participant, Lane, Role
from django.core.cache import cache

base_url_league_entries_by_summoner = "https://na1.api.riotgames.com/lol/league/v4/entries/by-summoner/"
base_url_match_lists_by_account = "https://na1.api.riotgames.com/lol/match/v4/matchlists/by-account/"
base_url_match_data = "https://na1.api.riotgames.com/lol/match/v4/matches/"
base_url_match_timeline_data = "https://na1.api.riotgames.com/lol/match/v4/timelines/by-match/"
LOWEST_MATCH_ID = 3257559899
WEEK_IN_SECONDS = 604800


@app.task(name='draftapp.tasks.update_database', max_retries=None, bind=True)
def update_database(self, lowest_rank, lowest_tier):
    rank_list = set()
    for rank in Rank:
        rank_list.add(rank)
        if rank == lowest_rank:
            break
    with transaction.atomic():
        summoners = Summoner.objects.filter(rank__in=rank_list, tier__gte=lowest_tier)
    for summoner in summoners:
        summ_id = summoner.summoner_id
        name = summoner.name
        acc_id = summoner.acc_id
        # Update each summoner and collect matches
        chain(fetch_summoner_data.signature(args=(summ_id,), queue='loldraft_api') |
              parse_summoner_data.signature(args=(name, summ_id), queue='loldraft') |
              update_summoner_data.signature(queue='loldraft')
              # collect_matches.signature(args=(name, acc_id,), queue='loldraft')
              ).apply_async()


@app.task(name='draftapp.tasks.collect_matches', max_retries=None, bind=True)
def collect_matches(self, data, summ_name, summ_acc_id):
    if not data:
        return
    if data["rank"] in ('PLATINUM', 'GOLD', 'SILVER', 'BRONZE', 'IRON', 'UNRANKED'):
        print("[///] Summoner " + summ_name + "'s rank(" + data["rank"] + ") is too low. Aborting.")
        return
    # Collect Match ID's from each summoner
    total_matches = data["total_matches"]
    total_matches if total_matches % 100 == 0 else total_matches + 100 - total_matches % 100
    for index in range(0, total_matches, 100):
        chain(fetch_match_list.signature(args=(summ_acc_id, index), queue='loldraft_api') |
              parse_match_list.signature(args=(summ_name,), queue='loldraft')
              ).apply_async()


@app.task(name='draftapp.tasks.parse_summoner_data', max_retires=None, bind=True, serializer='json')
def parse_summoner_data(self, data, name, summid):
    if not data:
        print("[-] Summoner " + name + "'s account unranked.")
        return_dict = {
            "summ_id": summid,
            "rank": "UNRANKED",
            "tier": "NOCHOICE",
            "total_matches": 0,
            "league_pts": 0,
            "name": name
        }
        return return_dict

    print("[+] Parsing summoner data for : " + name)
    for dictionary in data:
        if dictionary["queueType"] == "RANKED_SOLO_5x5":
            # Apparently I have rank and tier backwards... LMAO
            total_matches = dictionary["wins"] + dictionary["losses"]
            return_dict = {
                "summ_id": dictionary["summonerId"],
                "name": dictionary["summonerName"],
                "rank": dictionary["tier"],
                "tier": dictionary["rank"],
                "total_matches": total_matches,
                "league_pts": dictionary["leaguePoints"]
            }
            return return_dict
    else:
        print("[-] Summoner " + name + "'s account has no solo queue ranked games.")
        return_dict = {
            "summ_id": summid,
            "rank": "UNRANKED",
            "tier": "NOCHOICE",
            "total_matches": 0,
            "league_pts": 0,
            "name": name
        }
        return return_dict


@app.task(name='draftapp.tasks.fetch_summoner_data', max_retries=None, bind=True, serializer='json')
def fetch_summoner_data(self, summoner_id):
    with transaction.atomic():
        summoner = Summoner.objects.get(pk=summoner_id)

    rate_limit(self, 'loldraft')
    url = base_url_league_entries_by_summoner + summoner_id

    print("[+] Requesting Riot summoner data for : " + str(summoner) + " Rank: " + summoner.rank)
    data = consume_riot_api(self, url)

    return data


@app.task(name='draftapp.tasks.update_summoner_data', max_retries=None, bind=True, ignore_result=True)
def update_summoner_data(self, indict):
    if not indict:
        return

    print("[+] Updating summoner...")
    tier = indict["tier"]
    # JESUS CHRIST FIX THIS
    if tier == "I":
        tier = "ONE"
    elif tier == "II":
        tier = "TWO"
    elif tier == "III":
        tier = "THREE"
    elif tier == "IV":
        tier = "FOUR"
    Summoner.update_rank(indict["summ_id"], indict["rank"])
    Summoner.update_tier(indict["summ_id"], tier)
    Summoner.update_total_matches(indict["summ_id"], indict["total_matches"])
    Summoner.update_league_points(indict['summ_id'], indict["league_pts"])
    Summoner.update_name(indict["summ_id"], indict["name"])

    return indict


@app.task(name='draftapp.tasks.fetch_match_list', max_retries=None, bind=True)
def fetch_match_list(self, account_id, index):
    with transaction.atomic():
        summoner = Summoner.objects.get(acc_id=account_id)
    if summoner.rank in ('PLAT', 'GLD', 'SVR', 'BRZ', 'IRON'):
        print("[///] Summoner '" + str(summoner) + "' skipped. Rank: " + str(summoner.rank))
        return
    rate_limit(self, 'loldraft')
    url = base_url_match_lists_by_account + account_id + "?queue=420&beginIndex=" + str(index)

    print("[+] Finding all match IDs for summoner " + str(summoner) + "(" + summoner.rank + ") starting at index " +
          str(index))
    data = consume_riot_api(self, url)

    return data


@app.task(name='draftapp.tasks.parse_match_list', max_retries=None, bind=True)
def parse_match_list(self, data, name):
    if not data:
        return

    print("[+] Parsing match list for summoner : " + name)
    spawn_match_tasks = list()
    for dictionary in data["matches"]:
        if dictionary["gameId"] > LOWEST_MATCH_ID and dictionary["queue"] == 420:
            spawn_match_tasks.append(dictionary["gameId"])

    for match in spawn_match_tasks:
        chain(fetch_match_data.signature(args=(match,), queue='loldraft_api') |
              parse_match_data.signature(args=(match,), queue='loldraft') |
              fetch_match_timeline.signature(args=(match,), queue='loldraft_api') |
              parse_match_timeline.signature(args=(match,), queue='loldraft')
              ).apply_async()


@app.task(name='draftapp.tasks.fetch_match_data', max_retries=None, bind=True)
def fetch_match_data(self, match_id):
    if Match.objects.filter(pk=match_id).exists():
        print("[-] Match " + str(match_id) + " already processed!")
        # End the Chain of Tasks
        self.request.chain = None
        return

    rate_limit(self, 'loldraft')
    url = base_url_match_data + str(match_id)

    print("[+] Requesting Riot match data for match " + str(match_id))
    data = consume_riot_api(self, url)

    return data


@app.task(name='draftapp.tasks.parse_match_data', max_retries=None, bind=True, serializer='json')
def parse_match_data(self, data, match_id):
    if not data:
        print("[-] Match " + str(match_id) + " already processed or doesn't exist!")
        self.request.chain = None
        return

    print("[+] Parsing match data for : " + str(match_id))
    # Create Match
    if not Match.objects.filter(pk=match_id).exists():
        match_dict = {"platform": data["platformId"], "game_creation": localize_datetime(data["gameCreation"]),
                      "queue_id": data["queueId"], "season": data["seasonId"], "total_time": data["gameDuration"]}
        match_id = create_match(match_dict, match_id)
    else:
        print("[-] Match " + str(match_id) + " already processed!")
        self.request.chain = None
        return
    # List of Participant ID's to return
    ret_participant_dict = {}

    # Create Teams
    for dictionary in data["teams"]:
        team_dict = {"side": dictionary["teamId"], "win_or_lose": dictionary["win"]}
        team_id = create_team(team_dict, match_id)

        # Create Participants
        for pdict in data["participants"]:
            if dictionary["teamId"] == pdict["teamId"]:
                try:
                    primary_rune = pdict["stats"]["perk0"]
                except KeyError:
                    primary_rune = None
                try:
                    secondary_rune = pdict["stats"]["perkSubStyle"]
                except KeyError:
                    secondary_rune = None

                par_dict = {"pick_turn": pdict["participantId"], "role": pdict["timeline"]["role"],
                            "lane": pdict["timeline"]["lane"], "pick_id": pdict["championId"],
                            "ban_id": [bdict["championId"] for bdict in dictionary["bans"]
                                       if pdict["participantId"] == bdict["pickTurn"]][0],
                            "summoner_id": [idict["player"]["summonerId"] for idict in data["participantIdentities"]
                                            if pdict["participantId"] == idict["participantId"]][0],
                            "level": pdict["stats"]["champLevel"],
                            "kills": pdict["stats"]["kills"],
                            "deaths": pdict["stats"]["deaths"],
                            "assists": pdict["stats"]["assists"],
                            "items": [(pdict["stats"]["item" + str(i)]) for i in range(0, 6) if pdict["stats"]
                            ["item" + str(i)] != 0],
                            "spells": (pdict["spell1Id"], pdict["spell2Id"]),
                            "primary_rune": primary_rune,
                            "secondary_rune": secondary_rune,
                            "minions_killed": pdict["stats"]["totalMinionsKilled"]
                            }
                # verify if summoner exists
                if not Summoner.objects.filter(pk=par_dict["summoner_id"]).exists():
                    for participantdict in data["participantIdentities"]:
                        if par_dict["summoner_id"] == participantdict["player"]["summonerId"]:
                            summ_dict = {"summoner_id": par_dict["summoner_id"],
                                         "acc_id": participantdict["player"]["accountId"],
                                         "name": participantdict["player"]["summonerName"],
                                         "platform_id": participantdict["player"]["platformId"],
                                         }
                            create_summoner(summ_dict)

                ret_dict = create_participant(par_dict, team_id)
                for key in ret_dict.keys():
                    ret_participant_dict[key] = ret_dict[key]

    return ret_participant_dict


@app.task(name='draftapp.tasks.fetch_match_timeline', max_retries=None, bind=True)
def fetch_match_timeline(self, par_dict, match_id):
    if not par_dict:
        print("[-] Match " + str(match_id) + " already processed or doesn't exist!")
        self.request.chain = None
        return

    rate_limit(self, 'loldraft')
    url = base_url_match_timeline_data + str(match_id)

    print("[+] Requesting Riot match timeline data for match " + str(match_id))
    data = consume_riot_api(self, url)
    all_data = {**data, **par_dict}

    return all_data


@app.task(name='draftapp.tasks.parse_match_timeline', max_retries=None, bind=True)
def parse_match_timeline(self, data, match_id):
    if not data:
        print("[-] Match " + str(match_id) + " already processed or doesn't exist!")
        return

    print("[+] Parsing match timeline data for : " + str(match_id))
    junglers = resolve_junglers(data)
    supports = resolve_supports(data, junglers)
    top_laners = resolve_top_lane(data, junglers, supports)
    mid_laners = resolve_mid_lane(data, junglers, supports, top_laners)
    bot_laners = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    for jungler in junglers:
        jg_id = data[str(jungler)][0]
        Participant.update_role(jg_id, "NONE")
        Participant.update_lane(jg_id, "JUNGLE")
        bot_laners.remove(jungler)

    for support in supports:
        supp_id = data[str(support)][0]
        Participant.update_role(supp_id, "DUO_SUPPORT")
        Participant.update_lane(supp_id, "BOTTOM")
        bot_laners.remove(support)

    for top in top_laners:
        top_id = data[str(top)][0]
        Participant.update_role(top_id, "SOLO")
        Participant.update_lane(top_id, "TOP")
        bot_laners.remove(top)

    for mid in mid_laners:
        mid_id = data[str(mid)][0]
        Participant.update_role(mid_id, "SOLO")
        Participant.update_lane(mid_id, "MIDDLE")
        bot_laners.remove(mid)

    for bot in bot_laners:
        bot_id = data[str(bot)][0]
        Participant.update_role(bot_id, "DUO_CARRY")
        Participant.update_lane(bot_id, "BOTTOM")


# ------------------------ Update Bans Cache Tasks ------------------------#


@app.task(name='draftapp.tasks.calc_ban_ratio')
def calc_ban_ratio(res_dict, total_matches, champ_name):
    print("Calculating Ban Ratio.")
    bans_ratio = res_dict[champ_name]["num_bans"] / total_matches
    res_dict[champ_name]["bans_ratio"] = bans_ratio

    return res_dict


@app.task(name='draftapp.tasks.calc_num_picks', bind=True)
def calc_num_picks(self, res_dict, total_matches, champ_name, lane, role):
    if role == "":
        blue_num_picks = res_dict[champ_name][lane]["blue_wins"] + res_dict[champ_name][lane]["blue_loses"]
        red_num_picks = res_dict[champ_name][lane]["red_wins"] + res_dict[champ_name][lane]["red_loses"]

        res_dict[champ_name][lane]["blue_num_picks"] = blue_num_picks
        res_dict[champ_name][lane]["red_num_picks"] = red_num_picks
    else:
        blue_num_picks = res_dict[champ_name][lane][role]["blue_wins"] + res_dict[champ_name][lane][role]["blue_loses"]
        red_num_picks = res_dict[champ_name][lane][role]["red_wins"] + res_dict[champ_name][lane][role]["red_loses"]

        res_dict[champ_name][lane][role]["blue_num_picks"] = blue_num_picks
        res_dict[champ_name][lane][role]["red_num_picks"] = red_num_picks

    if inadequate_picks(blue_num_picks, total_matches):
        print(f"Inadequate number of picks ({blue_num_picks})...")
        return
    elif inadequate_picks(red_num_picks, total_matches):
        print(f"Inadequate number of picks ({red_num_picks})...")
        return

    print("calculating number of picks...")
    return res_dict


@app.task(name='draftapp.tasks.calc_pick_ratio')
def calc_pick_ratio(res_dict, total_matches, champ_name, lane, role):
    if not res_dict:
        return

    if role == "":
        blue_pick_ratio = res_dict[champ_name][lane]["blue_num_picks"] / total_matches
        red_pick_ratio = res_dict[champ_name][lane]["red_num_picks"] / total_matches

        res_dict[champ_name][lane]["blue_pick_ratio"] = blue_pick_ratio
        res_dict[champ_name][lane]["red_pick_ratio"] = red_pick_ratio
    else:
        blue_pick_ratio = res_dict[champ_name][lane][role]["blue_num_picks"] / total_matches
        red_pick_ratio = res_dict[champ_name][lane][role]["red_num_picks"] / total_matches

        res_dict[champ_name][lane][role]["blue_pick_ratio"] = blue_pick_ratio
        res_dict[champ_name][lane][role]["red_pick_ratio"] = red_pick_ratio

    print("Calculating pick ratio..")
    return res_dict


@app.task(name='draftapp.tasks.calc_win_rate')
def calc_win_rate(res_dict, total_matches, champ_name, lane, role):
    if not res_dict:
        return

    ban_weight = 1 + math.log((1 + (res_dict[champ_name]["num_bans"] / total_matches)), 10)

    # BLUE SIDE
    if role == "":
        num_absent = total_matches - res_dict[champ_name]["num_bans"] - res_dict[champ_name][lane]["blue_num_picks"]
        win_rate_lower, win_rate_upper = binconf(res_dict[champ_name][lane]["blue_wins"],
                                                 res_dict[champ_name][lane]["blue_loses"])
        win_rate_lower = adjust_win_rate(win_rate_lower, res_dict[champ_name][lane]["blue_num_picks"],
                                         res_dict[champ_name]["num_bans"], ban_weight, num_absent, total_matches)
        win_rate_upper = adjust_win_rate(win_rate_upper, res_dict[champ_name][lane]["blue_num_picks"],
                                         res_dict[champ_name]["num_bans"], ban_weight, num_absent, total_matches)
        win_rate = (win_rate_lower + win_rate_upper) / 2
        res_dict[champ_name][lane]["blue_win_rate"] = win_rate
    else:
        num_absent = total_matches - res_dict[champ_name]["num_bans"] - \
                     res_dict[champ_name][lane][role]["blue_num_picks"]
        win_rate_lower, win_rate_upper = binconf(res_dict[champ_name][lane][role]["blue_wins"],
                                                 res_dict[champ_name][lane][role]["blue_loses"])
        win_rate_lower = adjust_win_rate(win_rate_lower, res_dict[champ_name][lane][role]["blue_num_picks"],
                                         res_dict[champ_name]["num_bans"], ban_weight, num_absent, total_matches)
        win_rate_upper = adjust_win_rate(win_rate_upper, res_dict[champ_name][lane][role]["blue_num_picks"],
                                         res_dict[champ_name]["num_bans"], ban_weight, num_absent, total_matches)
        win_rate = (win_rate_lower + win_rate_upper) / 2
        res_dict[champ_name][lane][role]["blue_win_rate"] = win_rate

    # RED SIDE
    if role == "":
        num_absent = total_matches - res_dict[champ_name]["num_bans"] - res_dict[champ_name][lane]["red_num_picks"]
        win_rate_lower, win_rate_upper = binconf(res_dict[champ_name][lane]["red_wins"],
                                                 res_dict[champ_name][lane]["red_loses"])
        win_rate_lower = adjust_win_rate(win_rate_lower, res_dict[champ_name][lane]["red_num_picks"],
                                         res_dict[champ_name]["num_bans"], ban_weight, num_absent, total_matches)
        win_rate_upper = adjust_win_rate(win_rate_upper, res_dict[champ_name][lane]["red_num_picks"],
                                         res_dict[champ_name]["num_bans"], ban_weight, num_absent, total_matches)
        win_rate = (win_rate_lower + win_rate_upper) / 2
        res_dict[champ_name][lane]["red_win_rate"] = win_rate
    else:
        num_absent = total_matches - res_dict[champ_name]["num_bans"] - \
                     res_dict[champ_name][lane][role]["red_num_picks"]
        win_rate_lower, win_rate_upper = binconf(res_dict[champ_name][lane][role]["red_wins"],
                                                 res_dict[champ_name][lane][role]["red_loses"])
        win_rate_lower = adjust_win_rate(win_rate_lower, res_dict[champ_name][lane][role]["red_num_picks"],
                                         res_dict[champ_name]["num_bans"], ban_weight, num_absent, total_matches)
        win_rate_upper = adjust_win_rate(win_rate_upper, res_dict[champ_name][lane][role]["red_num_picks"],
                                         res_dict[champ_name]["num_bans"], ban_weight, num_absent, total_matches)
        win_rate = (win_rate_lower + win_rate_upper) / 2
        res_dict[champ_name][lane][role]["red_win_rate"] = win_rate

    return res_dict


@app.task(name='draftapp.tasks.dummy_callback', max_retries=None, bind=True)
def dummy_callback(self, results):
    print("Returning Results...")
    return results


@app.task(name='draftapp.tasks.query_num_loses')
def query_num_loses(res_dict, matches, champ_key, champ_name, lane, role):
    if role == "":
        blue_num_loses = Participant.objects.filter(team__match__in=matches, team__side=100, team__win_or_lose="fail",
                                                    pick_id=champ_key, lane=lane).count()
        red_num_loses = Participant.objects.filter(team__match__in=matches, team__side=200, team__win_or_lose="fail",
                                                   pick_id=champ_key, lane=lane).count()
        res_dict[champ_name][lane]["blue_loses"] = blue_num_loses
        res_dict[champ_name][lane]["red_loses"] = red_num_loses
    else:
        blue_num_loses = Participant.objects.filter(team__match__in=matches, team__side=100, team__win_or_lose="fail",
                                                    pick_id=champ_key, lane=lane, role=role).count()
        red_num_loses = Participant.objects.filter(team__match__in=matches, team__side=200, team__win_or_lose="fail",
                                                   pick_id=champ_key, lane=lane, role=role).count()
        res_dict[champ_name][lane][role]["blue_loses"] = blue_num_loses
        res_dict[champ_name][lane][role]["red_loses"] = red_num_loses

    print(f"\tChamp: {champ_name}\tBlue loses: {blue_num_loses} for lane: {lane}")
    print(f"\tChamp: {champ_name}\tRed loses: {red_num_loses} for lane: {lane}")
    return res_dict


@app.task(name='draftapp.tasks.query_num_wins')
def query_num_wins(res_dict, matches, champ_key, champ_name, lane, role):
    if role == "":
        blue_num_wins = Participant.objects.filter(team__match__in=matches, team__side=100, team__win_or_lose="win",
                                                   pick_id=champ_key, lane=lane).count()
        red_num_wins = Participant.objects.filter(team__match__in=matches, team__side=200, team__win_or_lose="win",
                                                  pick_id=champ_key, lane=lane).count()
        res_dict[champ_name][lane] = {}
        res_dict[champ_name][lane]["blue_wins"] = blue_num_wins
        res_dict[champ_name][lane]["red_wins"] = red_num_wins
    else:
        blue_num_wins = Participant.objects.filter(team__match__in=matches, team__side=100, team__win_or_lose="win",
                                                   pick_id=champ_key, lane=lane, role=role).count()
        red_num_wins = Participant.objects.filter(team__match__in=matches, team__side=200, team__win_or_lose="win",
                                                  pick_id=champ_key, lane=lane, role=role).count()
        try:
            res_dict[champ_name][lane][role] = {}
        except KeyError:
            res_dict[champ_name][lane] = {}
            res_dict[champ_name][lane][role] = {}

        res_dict[champ_name][lane][role]["blue_wins"] = blue_num_wins
        res_dict[champ_name][lane][role]["red_wins"] = red_num_wins

    print(f"\tChamp: {champ_name}\tBlue wins: {blue_num_wins} for lane: {lane}")
    print(f"\tChamp: {champ_name}\tRed wins: {red_num_wins} for lane: {lane}")
    return res_dict


@app.task(name='draftapp.tasks.query_num_bans', max_retries=None, bind=True)
def query_num_bans(self, matches, champ, champ_str, result_dict):
    num_bans = Participant.objects.filter(team__match__in=matches, ban_id=champ).count()
    result_dict[champ_str] = {}
    result_dict[champ_str]["num_bans"] = num_bans

    print(f"\tChamp:{champ_str}\t\tBans:{num_bans}")
    return result_dict


@app.task(name='draftapp.tasks.process_cached_dict', max_retries=None, bind=True)
def process_cached_dict(self, res_dict, rank, tier, patch):
    if tier is None:
        tier = ""
    new_dict = sort_dict(res_dict)
    json_data = json.dumps(new_dict, indent=4)
    cache.set(key=f"{rank}{tier}", value=json_data, timeout=None, version=patch)

    return "Done"


@app.task(name='draftapp.tasks.save_to_dict', max_retries=None, bind=True)
def save_to_dict(self, res_dict, champ, rank, tier, lane, role):
    if not res_dict:
        return

    if champ == "Nunu & Willump":
        champ_str = "Nunu"
    else:
        champ_str = champ

    cached_dict = {
        champ_str:
            {
                "blue":
                    {
                        lane: {}
                    },
                "red":
                    {
                        lane: {}
                    }
            }
    }
    for side in ["blue", "red"]:

        if side == "blue":
            if role == "":
                winrate = res_dict[champ][lane]["blue_win_rate"]
                pick_perc = res_dict[champ][lane]["blue_pick_ratio"]
            else:
                winrate = res_dict[champ][lane][role]["blue_win_rate"]
                pick_perc = res_dict[champ][lane][role]["blue_pick_ratio"]
        else:
            if role == "":
                winrate = res_dict[champ][lane]["red_win_rate"]
                pick_perc = res_dict[champ][lane]["red_pick_ratio"]
            else:
                winrate = res_dict[champ][lane][role]["red_win_rate"]
                pick_perc = res_dict[champ][lane][role]["red_pick_ratio"]

        cached_dict[champ_str][side][lane] = {
            "winrate": winrate,
            "banratio": res_dict[champ]["bans_ratio"] * 100,
            "pickratio": pick_perc * 100,
            "role": role,
            "score": calc_rank_score(winrate, pick_perc),
            "rank": rank,
            "tier": tier
        }

    print(f"Successfully updated champion {champ_str} - {lane}:{role}")
    return cached_dict


# ------------------------ Views Tasks ------------------------#

@app.task(name='draftapp.tasks.query_picks', max_retries=None, bind=True)
def query_picks(self, side, dictionary):

    if side == "red":
        side_int = 200
    else:
        side_int = 100

    matches = Match.objects.all()
    for key in dictionary:
        query_side = get_team_side(key)
        lane = Lane_Dict[dictionary[key][1]]
        if lane == "":
            matches = matches.filter(team__side=query_side, team__participant__pick_id=dictionary[key][0])
        elif lane == "SUP":
            matches = matches.filter(team__side=query_side, team__participant__pick_id=dictionary[key][0],
                                     team__participant__role=Role.DUO_SUPPORT)
        else:
            lane = Lane(lane)
            matches = matches.filter(team__side=query_side, team__participant__pick_id=dictionary[key][0],
                                     team__participant__lane=lane)
    totals = matches.filter(team__side=side_int).values_list('team__win_or_lose', 'team__participant__pick_id',
                                                             'team__participant__lane', 'team__participant__role')
    champ_list = process_pick_data(totals)
    return champ_list
