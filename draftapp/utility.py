import math
import time
import datetime
from ast import literal_eval
from collections import Counter

import requests
import json
from django.db import transaction

from lib.utility_lists import RED_LIST, BLUE_LIST
from typing import Dict

from loldraft import settings
from loldraft.settings import load_dotenv, os
from django.utils import timezone
from draftapp.models import Match, Tier, Rank, Team, Summoner, Champion, SummonerRune, Participant
from django.core.cache import cache
from lib.utility_dicts import Rank_Dict, Tier_Dict
from lib import utility_classes

RANK_LIST = ["DMD", "MR", "GMR", "CHR"]
TIER_LIST = ["IV", "III", "II", "I", ""]
LANE_LIST = [("TOP", ""), ("JG", ""), ("MID", ""), ("BOT", "CARRY"), ("BOT", "SUPPORT")]


# ------------------------ Update Database Utility ------------------------ #
def check_if_both_supps_bot(data, supp_one, supp_two):
    supp_one_cs = supp_two_cs = 0

    # check end game CS
    for par_dict in data["frames"][-1]["participantFrames"]:

        if supp_one == data["frames"][-1]["participantFrames"][par_dict]["participantId"]:
            supp_one_cs = data["frames"][-1]["participantFrames"][par_dict]["minionsKilled"] + \
                          data["frames"][-1]["participantFrames"][par_dict]["jungleMinionsKilled"]

        if supp_two == data["frames"][-1]["participantFrames"][par_dict]["participantId"]:
            supp_two_cs = data["frames"][-1]["participantFrames"][par_dict]["minionsKilled"] + \
                          data["frames"][-1]["participantFrames"][par_dict]["jungleMinionsKilled"]

    if supp_one <= 5 and supp_two <= 5:
        if supp_two_cs > supp_one_cs:
            return True
        return False
    else:
        if supp_two_cs > supp_one_cs:
            return True
        return False


def check_if_midlaner(data, target_id, supp_list):
    mid_count_dict = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0}

    for index in range(0, 10, 1):
        try:
            dictt = data["frames"][index]
            for key in dictt["participantFrames"].keys():
                if abs(dictt["participantFrames"][key]["position"]["x"] -
                       dictt["participantFrames"][key]["position"]["y"]) < 1000:
                    mid_count_dict[str(dictt["participantFrames"][key]["participantId"])] += 1
        except (KeyError, IndexError):
            pass
    for par_id in supp_list:
        if mid_count_dict[str(target_id)] > mid_count_dict[str(par_id)] and target_id != par_id:
            return True
        elif mid_count_dict[str(target_id)] < mid_count_dict[str(par_id)] and target_id != par_id:
            return False

    return False


def consume_riot_api(task, url):
    api = load_api()
    try:
        headers = {"X-Riot-Token": api}
        response = requests.get(url, headers=headers, timeout=5.0)

        print("....[!] Rate limit count: " + response.headers['X-App-Rate-Limit-Count'])

        response.raise_for_status()
        data = json.loads(response.text)
        return data

    except requests.HTTPError as error:

        if error.response.status_code == 400:
            print("[-] 400 error: Bad Request")
            return
        elif error.response.status_code == 403:
            print("[-] 403 Error: API Key's time limit has ran out. Shutting down all workers...")
            task.app.control.shutdown()
        elif error.response.status_code == 404:
            print("[-] 404 Error: Requested data not found. Deleting task...")
            return
        elif error.response.status_code == 429:
            print("[-] 429 Error: Too many requests. Sleeping worker for 30 seconds.")
            time.sleep(30)
            task.retry(queue='loldraft_api')
        elif error.response.status_code == 503:
            print("[-] 503 Error: Service Unavailable. Retrying in 5 seconds...")
            task.retry(error=error, countdown=5.0, queue='loldraft_api')
        elif error.response.status_code == 504:
            print("[-] 504 Error: Gateway Unavailable. Retrying in 5 seconds...")
            task.retry(error=error, countdown=5.0, queue='loldraft_api')
        else:
            print(error)
            print(error.response)
            time.sleep(30)
            task.retry(error=error, queue='loldraft_api')


def create_match(matchdict, match_id):
    with transaction.atomic():
        match = Match.objects.create(match_id=match_id, platform_id=matchdict["platform"],
                                     game_creation=matchdict["game_creation"],
                                     queue_id=matchdict["queue_id"], season=matchdict["season"], average_rank=Rank.IRON,
                                     average_tier=Tier.NOCHOICE, total_time=matchdict["total_time"])
        match.save()
    return match.match_id


def create_participant(pardict, team_id):
    with transaction.atomic():
        team = Team.objects.get(pk=team_id)
        summoner = Summoner.objects.get(pk=pardict["summoner_id"])
        champ_pick = Champion.objects.get(key=pardict["pick_id"])
        if pardict["ban_id"] is not None and pardict["ban_id"] != -1:
            champ_ban = Champion.objects.get(key=pardict["ban_id"])
        else:
            champ_ban = None
        if pardict["primary_rune"]:
            p_rune = SummonerRune.objects.get(pk=pardict["primary_rune"])
        else:
            p_rune = None
        if pardict["secondary_rune"]:
            s_rune = SummonerRune.objects.get(pk=pardict["secondary_rune"])
        else:
            s_rune = None

        participant = Participant.objects.create(team=team, pick_turn=pardict["pick_turn"], role=pardict["role"],
                                                 lane=pardict["lane"], pick_id=champ_pick, ban_id=champ_ban,
                                                 summoner_id=summoner, rank=summoner.rank, tier=summoner.tier,
                                                 level=pardict["level"], kills=pardict["kills"],
                                                 deaths=pardict["deaths"], assists=pardict["assists"],
                                                 primary_rune=p_rune, secondary_rune=s_rune,
                                                 minions_killed=pardict["minions_killed"])
        for item in pardict["items"]:
            participant.items.add(item)
        for spell in pardict["spells"]:
            participant.spells.add(spell)
        participant.save()
        ret_dict = {str(participant.pick_turn): (participant.participant_id, participant.pick_id.key,
                                                 participant.pick_id.name)}

    return ret_dict


def create_summoner(summdict):
    with transaction.atomic():
        summoner = Summoner.objects.create(summoner_id=summdict["summoner_id"], acc_id=summdict["acc_id"],
                                           name=summdict["name"], platform_id=summdict["platform_id"],
                                           total_matches=0,
                                           rank=Rank.CHALLENGER, tier=Tier.NOCHOICE, league_points=0)
        summoner.save()
    print("[+++] New summoner " + str(summoner) + " created!")
    return


def create_team(teamdict, match_id):
    with transaction.atomic():
        match = Match.objects.get(pk=match_id)
        team = Team.objects.create(match=match, side=teamdict["side"], win_or_lose=teamdict["win_or_lose"])
        team.save()
    return team.team_id


def find_afk_summoner(data):
    afk_supports = list()
    par_id_dic = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, "9": 0, "10": 0}
    for index in range(0, 10, 1):
        try:
            dictt = data["frames"][index]
            for event in dictt["events"]:
                par_id_dic[str(event["participantId"])] += 1
        except (KeyError, IndexError):
            pass
    for key in par_id_dic.keys():
        if par_id_dic[key] == 0:
            return int(key)
    else:
        dictt = data["frames"][-1]
        [afk_supports.append(str(frame["participantId"])) for frame in dictt["participantFrames"] if
         frame["level"] == 1]
        return afk_supports[0]


def load_api():
    load_dotenv()
    api = os.getenv("API").rstrip()
    return api


def localize_datetime(dt):
    base_datetime = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(dt / 1000))
    naive_datetime = datetime.datetime.strptime(base_datetime, "%Y-%m-%d %H:%M:%S")
    current_tz = timezone.get_current_timezone()
    return current_tz.localize(naive_datetime)


def resolve_junglers(data):
    junglers = list()

    for index in range(0, 10, 1):
        try:
            dictt = data["frames"][index]

            [junglers.append(event["participantId"]) for event in dictt["events"] if event["type"] ==
             "ITEM_PURCHASED" and event["itemId"] in (1039, 1041)]
            [junglers.remove(event["participantId"]) for event in dictt["events"] if event["type"] == "ITEM_UNDO"
             and event["beforeId"] in (1039, 1041)]
            [junglers.remove(event["participantId"]) for event in dictt["events"] if event["type"] == "ITEM_SOLD"
             and event["itemId"] in (1039, 1041)]
            # At 2 minutes
            if index == 2:
                [junglers.append(dictt["participantFrames"][key]["participantId"]) for key in
                 dictt["participantFrames"].keys() if dictt["participantFrames"][key]["jungleMinionsKilled"] > 1]

            # At 3 minutes
            if index == 3:
                [junglers.append(dictt["participantFrames"][key]["participantId"]) for key in
                 dictt["participantFrames"].keys() if dictt["participantFrames"][key]["jungleMinionsKilled"] > 4]
        except (KeyError, IndexError):
            pass

        if len(set(junglers)) == 2:
            return set(junglers)

    for element in junglers:
        if not junglers.count(element) >= 2:
            junglers.remove(element)

    return set(junglers)


def resolve_mid_lane(data, jglers, supps, tops):
    mid_count_blue_side = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    mid_count_red_side = {"6": 0, "7": 0, "8": 0, "9": 0, "10": 0}

    for jg in jglers:
        mid_count_red_side.pop(str(jg), None)
        mid_count_blue_side.pop(str(jg), None)

    for supp in supps:
        mid_count_red_side.pop(str(supp), None)
        mid_count_blue_side.pop(str(supp), None)

    for top in tops:
        mid_count_red_side.pop(str(top), None)
        mid_count_blue_side.pop(str(top), None)

    for index in range(0, 10, 1):
        try:
            dictt = data["frames"][index]
            for key in dictt["participantFrames"].keys():
                # Blue Side
                if dictt["participantFrames"][key]["participantId"] <= 5:
                    if abs(dictt["participantFrames"][key]["position"]["x"] -
                           dictt["participantFrames"][key]["position"]["y"]) < 1000:
                        mid_count_blue_side[str(dictt["participantFrames"][key]["participantId"])] += 1
                # Red Side
                else:
                    if abs(dictt["participantFrames"][key]["position"]["x"] -
                           dictt["participantFrames"][key]["position"]["y"]) < 1000:
                        mid_count_red_side[str(dictt["participantFrames"][key]["participantId"])] += 1
        except (KeyError, IndexError):
            pass

    blue_mid = int(max(mid_count_blue_side, key=mid_count_blue_side.get))
    red_mid = int(max(mid_count_red_side, key=mid_count_red_side.get))

    ret_list = (blue_mid, red_mid)

    return set(ret_list)


def resolve_niche_supp_picks(data, supp_list):
    for supp in supp_list:
        if check_if_midlaner(data, supp, supp_list):
            return supp
    if check_if_both_supps_bot(data, supp_list[0], supp_list[1]):
        return supp_list[0]
    elif check_if_both_supps_bot(data, supp_list[1], supp_list[0]):
        return supp_list[1]


def resolve_supports(data, jglers):
    supports = list()

    # First 9 minutes
    for index in range(0, 10, 1):
        try:
            dictt = data["frames"][index]
            [supports.append(event["participantId"]) for event in dictt["events"] if event["type"] ==
             "ITEM_PURCHASED" and event["itemId"] in (3850, 3854, 3858, 3862)]
            [supports.remove(event["participantId"]) for event in dictt["events"] if event["type"] == "ITEM_UNDO"
             and event["beforeId"] in (3850, 3854, 3858, 3862)]
            [supports.remove(event["participantId"]) for event in dictt["events"] if event["type"] == "ITEM_SOLD"
             and event["itemId"] in (3850, 3854, 3858, 3862)]
        except (KeyError, IndexError):
            pass
    # Remove Junglers from the list
    for jg in jglers:
        if jg in supports:
            supports.remove(jg)

    # Find AFK support and add
    if len(set(supports)) < 2:
        afk_summoner = find_afk_summoner(data)
        supports.append(afk_summoner)

    if len(set(supports)) == 2:
        return set(supports)

    if len(set(supports)) > 2:
        # Resolve two supports on same team
        blue_list = list()
        [blue_list.append(value) for index, value in enumerate(supports) if value <= 5]
        if len(blue_list) == 2:
            dirty_support = resolve_niche_supp_picks(data, blue_list)
            supports.remove(dirty_support)

        red_list = list()
        [red_list.append(value) for index, value in enumerate(supports) if value > 5]
        if len(red_list) == 2:
            dirty_support = resolve_niche_supp_picks(data, red_list)
            supports.remove(dirty_support)

        return set(supports)

    return set(supports)


def resolve_top_lane(data, jglers, supps):
    top_count_blue_side = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
    top_count_red_side = {"6": 0, "7": 0, "8": 0, "9": 0, "10": 0}

    for jg in jglers:
        top_count_red_side.pop(str(jg), None)
        top_count_blue_side.pop(str(jg), None)

    for supp in supps:
        top_count_red_side.pop(str(supp), None)
        top_count_blue_side.pop(str(supp), None)

    for index in range(0, 10, 1):
        try:
            dictt = data["frames"][index]
            for key in dictt["participantFrames"].keys():
                # Blue Side
                if dictt["participantFrames"][key]["participantId"] <= 5:
                    if dictt["participantFrames"][key]["position"]["x"] <= 10000 and \
                            dictt["participantFrames"][key]["position"]["y"] >= 9000:
                        top_count_blue_side[str(dictt["participantFrames"][key]["participantId"])] += 1

                # Red Side
                else:
                    if dictt["participantFrames"][key]["position"]["x"] <= 10000 and \
                            dictt["participantFrames"][key]["position"]["y"] >= 9000:
                        top_count_red_side[str(dictt["participantFrames"][key]["participantId"])] += 1
        except (KeyError, IndexError):
            pass
    blue_top = int(max(top_count_blue_side, key=top_count_blue_side.get))
    red_top = int(max(top_count_red_side, key=top_count_red_side.get))

    ret_list = (blue_top, red_top)

    return set(ret_list)


# ------------------------ Update Bans Cache Utility ------------------------ #
def adjust_win_rate(win_rate, picks, bans, ban_weight, absent, total):
    adjusted_win_rate = ((win_rate * picks) + (win_rate * bans * ban_weight) + (win_rate * absent)) / total
    adjusted_win_rate = adjusted_win_rate * 100

    return adjusted_win_rate


def binconf(p, n, c=0.95):
    """
  Calculate binomial confidence interval based on the number of positive and
  negative events observed.  Uses Wilson score and approximations to inverse
  of normal cumulative density function.

  Parameters
  ----------
  p: int
      number of positive events observed
  n: int
      number of negative events observed
  c : optional, [0,1]
      confidence percentage. e.g. 0.95 means 95% confident the probability of
      success lies between the 2 returned values

  Returns
  -------
  theta_low  : float
      lower bound on confidence interval
  theta_high : float
      upper bound on confidence interval
  """
    p, n = float(p), float(n)
    N = p + n

    if N == 0.0:
        return 0.0, 1.0

    p = p / N
    z = normcdfi(1 - 0.5 * (1 - c))

    a1 = 1.0 / (1.0 + z * z / N)
    a2 = p + z * z / (2 * N)
    a3 = z * math.sqrt(p * (1 - p) / N + z * z / (4 * N * N))

    return a1 * (a2 - a3), a1 * (a2 + a3)


def calc_rank_score(winrate, pickrate):
    pick_log = math.log(1 + pickrate)
    score = winrate * (1 + pick_log)
    return score


def clear_cache_dict(dictionary):
    dictionary["blue"].clear()
    dictionary["red"].clear()
    return dictionary


def erfi(x):
    """Approximation to inverse error function"""
    a = 0.147  # MAGIC!!!
    a1 = math.log(1 - x * x)
    a2 = (2.0 / (math.pi * a) + a1 / 2.0)

    return sign(x) * math.sqrt(math.sqrt(a2 * a2 - a1 / a) - a2)


def filter_match_by_patch(self, index, queryset):
    patch_datetime_obj = get_patch_date(index)
    new_queryset = queryset.exclude(game_creation__lt=patch_datetime_obj)
    self.stdout.write(self.style.SUCCESS(f"Parsing queryset for patch {index}+"))
    return new_queryset


def get_champ_list():
    champ_list = []
    champ_set = list(Champion.objects.all().values_list('key', 'name'))
    for champ in champ_set:
        for lane_role in LANE_LIST:
            champ_list.append([champ[0], champ[1], lane_role[0], lane_role[1]])
    return champ_list, champ_set


def get_match_qs(rank, tier, index):
    patch_datetime_obj = get_patch_date(index)
    ranks = list(RANK_LIST[RANK_LIST.index(rank):])
    if not tier:
        matches = Match.objects.filter(average_rank__in=ranks).exclude(game_creation__lt=patch_datetime_obj) \
            .values_list('match_id', flat=True)
    else:
        tiers = TIER_LIST[TIER_LIST.index(tier):]
        matches = Match.objects.filter(average_rank__in=ranks).exclude(game_creation__lt=patch_datetime_obj) \
            .filter(average_tier__in=tiers).values_list('match_id', flat=True)

    return list(matches), matches.count()


def get_patch_date(patch):
    patch_date_obj = datetime.datetime.strptime(utility_classes.Patch(patch).value, '%Y-%m-%d %H:%M:%S')
    current_tz = timezone.get_current_timezone()
    return current_tz.localize(patch_date_obj)


def get_score(data):
    score = float((list(list(data.values())[0].values())[0]['score']))
    return score


def inadequate_picks(picks, total_matches):
    if total_matches > 100000 and picks >= 1000:
        return False

    elif total_matches > 50000 and picks >= 500:
        return False

    elif total_matches < 50000 and picks >= 100:
        return False

    return True


def normcdfi(p, mu=0.0, sigma2=1.0):
    """Inverse CDF of normal distribution"""
    if mu == 0.0 and sigma2 == 1.0:
        return math.sqrt(2) * erfi(2 * p - 1)
    else:
        return mu + math.sqrt(sigma2) * normcdfi(p)


def sign(x):
    if x < 0:
        return -1
    if x == 0:
        return 0
    if x > 0:
        return 1


def sort_dict(dictionary):
    new_dict = {}
    for dictt in dictionary:
        if dictt is not None:
            for key, value in dictt.items():
                tmp_dict = {key: value}
                if key in new_dict:
                    new_dict[key]['blue'] = dict(new_dict[key]['blue'], **tmp_dict[key]['blue'])
                    new_dict[key]['red'] = dict(new_dict[key]['red'], **tmp_dict[key]['red'])
                else:
                    new_dict = dict(new_dict, **tmp_dict)

    blue_data_list = list()
    red_data_list = list()
    for dictt in new_dict:
        if len(new_dict[dictt][list(new_dict[dictt].keys())[0]].keys()) > 1:
            for i in range(0, len(new_dict[dictt][list(new_dict[dictt].keys())[0]].keys())):
                blue_key = [list(new_dict[dictt].keys())[0]][0]
                red_key = [list(new_dict[dictt].keys())[1]][0]
                blue_role_key = [list(new_dict[dictt][blue_key].keys())[i]][0]
                red_role_key = [list(new_dict[dictt][red_key].keys())[i]][0]
                tmp_blue_dict = {dictt: {blue_role_key: new_dict[dictt][blue_key][blue_role_key]}}
                tmp_red_dict = {dictt: {red_role_key: new_dict[dictt][red_key][red_role_key]}}
                blue_data_list.append(tmp_blue_dict)
                red_data_list.append(tmp_red_dict)
        else:
            blue_data_list.append({dictt: new_dict[dictt][list(new_dict[dictt].keys())[0]]})
            red_data_list.append({dictt: new_dict[dictt][list(new_dict[dictt].keys())[1]]})
    blue_data_list.sort(key=get_score, reverse=True)
    red_data_list.sort(key=get_score, reverse=True)
    re_ordered_dict = {
        "blue": blue_data_list,
        "red": red_data_list
    }
    return re_ordered_dict


# ------------------------ Views Utility ------------------------ #
def champ_str_to_id(champ_str) -> int:

    champ_id = Champion.objects.filter(name=champ_str).values_list('key', flat=True)[0]
    return champ_id


def champ_id_to_str(key) -> str:
    """
    Takes a given Champion Model's key and returns the respective Champion's name.
    :param key: A Champion Model key.
    :return: str: A Champion Model name.
    """
    return str(Champion.objects.get(key=key))


def clean_pick_dictionary(dict_str: str) -> dict:
    """
    Takes a JSON string and transforms it into a dictionary.
    :param dict_str: A JSON string
    :return: dict: An equivalent dictionary - replacing champion names with their respective keys
    """
    ret_dict = {}
    dict_str = literal_eval(dict_str)
    for key in dict_str:
        champ = dict_str[key][0]
        role = dict_str[key][1]
        if champ == "":
            continue
        ret_dict[key] = [champ_str_to_id(champ), ""]
        if role == "utility":
            ret_dict[key][1] = "support"
            continue
        ret_dict[key][1] = role
    return ret_dict


def getimagedict() -> dict:
    """
    Returns a dictionary of all images from the static folder in rows of 8.
    :return: dict: A dict of all image file paths in the static directory
    """
    image_dic = {}
    file_imgs = os.listdir(os.path.join(settings.IMAGE_ROOT, "champion"))
    file_imgs.sort()
    counter = 0
    for img in file_imgs:
        image_dic.setdefault(counter, []).append("/static/img/champion/" + img)
        if counter == 0 and len(image_dic[counter]) == 1:
            image_dic.setdefault(counter, []).insert(0, "/static/img/positions/icon-position-none-disabled.png")
        if len(image_dic[counter]) == 8:
            counter += 1
    return image_dic


def getpatchdict():
    patch_dict = {
        "10.21": "10-11-2020",
        "10.20": "9-30-2020",
        "10.19": "9-16-2020",
        "10.18": "9-2-2020",
        "10.17": "8-19-2020",
        "10.16": "8-5-2020",
        "10.15": "7-22-2020",
        "10.14": "7-8-2020"
    }
    return patch_dict


def getpatchrequest(request):
    if request is None:
        return
    return int(request.split(" ")[0][3:])


def getrankrequest(request):
    if request is None:
        return
    return f"{Rank_Dict[request.split(' ')[0]]}{Tier_Dict[request.split(' ')[1]]}"


def getwinrate(data):
    winrate = list(list(data.values())[0].items())[0][1][0]
    return winrate


def get_team_side(key):
    if key in RED_LIST:
        query_side = 200
    elif key in BLUE_LIST:
        query_side = 100
    else:
        query_side = 100
    return query_side


def load_cache(rank=None, patch=None):
    if not rank:
        return json.loads(cache.get('DMDIV', version=1))
    else:
        return json.loads(cache.get(rank, version=patch))


def process_pick_data(data_list):
    totals_total = Counter(
        [
            (data[1], data[2]) if data[2] in ["TOP"]
            else (data[1], "JG") if data[2] in ["JUNGLE", "JG"]
            else (data[1], "MID") if data[2] in ["MIDDLE", "MID"]
            else (data[1], "SUPPORT") if data[3] in ["DUO_SUPPORT", "SUPPORT"]
            else (data[1], "CARRY")
            for data in data_list if data[1] is not None
        ])
    wins_total = Counter(
        [
            (data[1], data[2]) if data[2] in ["TOP"]
            else (data[1], "JG") if data[2] in ["JUNGLE", "JG"]
            else (data[1], "MID") if data[2] in ["MIDDLE", "MID"]
            else (data[1], "SUPPORT") if data[3] in ["DUO_SUPPORT", "SUPPORT"]
            else (data[1], "CARRY")
            for data in data_list if data[0] == "Win" and data[1] is not None
        ])
    champ_list = list()
    [
        champ_list.append(
            {
                champ_id_to_str(key[0]):
                    {
                        key[1]: [(wins_total[key] / totals_total[key]) * 100, wins_total[key], totals_total[key]]
                    }
            }) for key in totals_total if totals_total[key] > 10 and key[1] is not None
    ]
    champ_list.sort(key=getwinrate, reverse=True)

    return champ_list
