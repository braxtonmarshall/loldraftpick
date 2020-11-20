from django.test import TestCase
from .models import *


class MatchModelTests(TestCase):

    def test_create_match(self):
        match = create_match(1)
        self.assertTrue(isinstance(match, Match))
        self.assertEqual(match.match_id, 1)
        self.assertEqual(match.platform_id, Platform.NORTH_AMERICA)
        self.assertEqual(match.game_creation, "2020-09-12")
        self.assertEqual(match.queue_id, Queue.RANKED_SOLO_5v5)
        self.assertEqual(match.season, 13)
        self.assertEqual(match.average_rank, Rank.DIAMOND)
        self.assertEqual(match.average_tier, Tier.THREE)
        self.assertEqual(match.total_time, 1440)

    def test_clean_tier(self):
        match = create_match(2)
        match.average_rank = Rank.CHALLENGER
        match.save()

        self.assertTrue(isinstance(match, Match))
        self.assertEqual(match.match_id, 2)
        self.assertEqual(match.platform_id, Platform.NORTH_AMERICA)
        self.assertEqual(match.game_creation, "2020-09-12")
        self.assertEqual(match.queue_id, Queue.RANKED_SOLO_5v5)
        self.assertEqual(match.season, 13)
        self.assertEqual(match.average_rank, Rank.CHALLENGER)
        self.assertEqual(match.average_tier, Tier.NOCHOICE)
        self.assertEqual(match.total_time, 1440)


class TeamModelTests(TestCase):

    def test_create_team(self):
        match = create_match(3)
        team = create_team(match)
        self.assertTrue(isinstance(team, Team))
        self.assertTrue(isinstance(team.match, Match))
        self.assertEqual(team.team_id, 4)
        self.assertEqual(team.match, match)
        self.assertEqual(team.side, Team.Side.BLUE)
        self.assertEqual(team.side, 100)
        self.assertEqual(team.win_or_lose, "Lose")

    def test_team_to_string(self):
        match = create_match(4)
        team = create_team(match)
        self.assertTrue(isinstance(team, Team))
        self.assertTrue(isinstance(team.match, Match))
        self.assertEqual(team.team_id, 5)
        self.assertEqual(team.match, match)
        self.assertEqual(team.side, Team.Side.BLUE)
        self.assertEqual(team.side, 100)
        self.assertEqual(team.win_or_lose, "Lose")
        self.assertEqual(str(team), str(team.team_id))
        self.assertEqual(str(team), str(5))


class ChampionModelTests(TestCase):

    def test_create_champion(self):
        champ = create_champion(1)
        self.assertTrue(isinstance(champ, Champion))
        self.assertEqual(champ.key, 1)
        self.assertEqual(champ.champ_id, "Annie")
        self.assertEqual(champ.name, "Annie")
        self.assertEqual(champ.img, "Annie.png")

    def test_champion_to_string(self):
        champ = create_champion(2)
        self.assertTrue(isinstance(champ, Champion))
        self.assertEqual(str(champ), str(champ.name))
        self.assertEqual(str(champ), "Annie")


class SummonerModelTests(TestCase):

    def test_create_summoner(self):
        summoner = create_summoner("1000", "xx10")
        self.assertTrue(isinstance(summoner, Summoner))
        self.assertEqual(summoner.summoner_id, "1000")
        self.assertEqual(summoner.acc_id, "xx10")
        self.assertEqual(summoner.name, "Big AD")
        self.assertEqual(summoner.platform_id, Platform.NORTH_AMERICA)
        self.assertEqual(summoner.total_matches, 1000)
        self.assertEqual(summoner.rank, Rank.DIAMOND)
        self.assertEqual(summoner.tier, Tier.FOUR)
        self.assertEqual(summoner.league_points, 0)

    def test_clean_model(self):
        summoner = create_summoner("2000", "xx20")
        summoner.rank = Rank.MASTER
        summoner.save()

        self.assertTrue(isinstance(summoner, Summoner))
        self.assertEqual(summoner.summoner_id, "2000")
        self.assertEqual(summoner.acc_id, "xx20")
        self.assertEqual(summoner.name, "Big AD")
        self.assertEqual(summoner.platform_id, Platform.NORTH_AMERICA)
        self.assertEqual(summoner.total_matches, 1000)
        self.assertEqual(summoner.rank, Rank.MASTER)
        self.assertEqual(summoner.tier, Tier.NOCHOICE)
        self.assertEqual(summoner.league_points, 0)

    def test_update_name(self):
        summoner = create_summoner("3000", "xx30")
        summoner = Summoner.update_name(summ_id=summoner.summoner_id, new_name="Big Penis")

        self.assertTrue(isinstance(summoner, Summoner))
        self.assertEqual(summoner.summoner_id, "3000")
        self.assertEqual(summoner.acc_id, "xx30")
        self.assertEqual(summoner.name, "Big Penis")
        self.assertEqual(summoner.platform_id, Platform.NORTH_AMERICA)
        self.assertEqual(summoner.total_matches, 1000)
        self.assertEqual(summoner.rank, Rank.DIAMOND)
        self.assertEqual(summoner.tier, Tier.FOUR)
        self.assertEqual(summoner.league_points, 0)

    def test_update_total_match(self):
        summoner = create_summoner("4000", "xx40")
        summoner = Summoner.update_total_matches(summ_id=summoner.summoner_id, matches=2000)

        self.assertTrue(isinstance(summoner, Summoner))
        self.assertEqual(summoner.summoner_id, "4000")
        self.assertEqual(summoner.acc_id, "xx40")
        self.assertEqual(summoner.name, "Big AD")
        self.assertEqual(summoner.platform_id, Platform.NORTH_AMERICA)
        self.assertEqual(summoner.total_matches, 2000)
        self.assertEqual(summoner.rank, Rank.DIAMOND)
        self.assertEqual(summoner.tier, Tier.FOUR)
        self.assertEqual(summoner.league_points, 0)

    def test_update_rank(self):
        summoner = create_summoner("5000", "xx50")
        summoner = Summoner.update_rank(summ_id=summoner.summoner_id, new_rank="MASTER")

        self.assertTrue(isinstance(summoner, Summoner))
        self.assertEqual(summoner.summoner_id, "5000")
        self.assertEqual(summoner.acc_id, "xx50")
        self.assertEqual(summoner.name, "Big AD")
        self.assertEqual(summoner.platform_id, Platform.NORTH_AMERICA)
        self.assertEqual(summoner.total_matches, 1000)
        self.assertEqual(summoner.rank, Rank.MASTER)
        self.assertEqual(summoner.tier, Tier.NOCHOICE)
        self.assertEqual(summoner.league_points, 0)

    def test_update_tier(self):
        summoner = create_summoner("6000", "xx60")
        summoner = Summoner.update_tier(summ_id=summoner.summoner_id, new_tier="THREE")

        self.assertTrue(isinstance(summoner, Summoner))
        self.assertEqual(summoner.summoner_id, "6000")
        self.assertEqual(summoner.acc_id, "xx60")
        self.assertEqual(summoner.name, "Big AD")
        self.assertEqual(summoner.platform_id, Platform.NORTH_AMERICA)
        self.assertEqual(summoner.total_matches, 1000)
        self.assertEqual(summoner.rank, Rank.DIAMOND)
        self.assertEqual(summoner.tier, Tier.THREE)
        self.assertEqual(summoner.league_points, 0)

    def test_update_league_points(self):
        summoner = create_summoner("7000", "xx70")
        summoner = Summoner.update_league_points(summ_id=summoner.summoner_id, new_points=15)

        self.assertTrue(isinstance(summoner, Summoner))
        self.assertEqual(summoner.summoner_id, "7000")
        self.assertEqual(summoner.acc_id, "xx70")
        self.assertEqual(summoner.name, "Big AD")
        self.assertEqual(summoner.platform_id, Platform.NORTH_AMERICA)
        self.assertEqual(summoner.total_matches, 1000)
        self.assertEqual(summoner.rank, Rank.DIAMOND)
        self.assertEqual(summoner.tier, Tier.FOUR)
        self.assertEqual(summoner.league_points, 15)

    def test_summoner_to_string(self):
        summoner = create_summoner("10000", "xx1000")
        self.assertTrue(isinstance(summoner, Summoner))
        self.assertEqual(str(summoner), summoner.name)
        self.assertEqual(str(summoner), "Big AD")


class SummonerSpellModelTests(TestCase):

    def test_create_summoner_sell(self):
        summspell = create_summonerspell(100, "SummonerFlash", "Flash")
        self.assertTrue(isinstance(summspell, SummonerSpell))
        self.assertEqual(summspell.key, 100)
        self.assertEqual(summspell.id, "SummonerFlash")
        self.assertEqual(summspell.name, "Flash")
        self.assertEqual(summspell.description, "Teleports your champion a short distance.")
        self.assertEqual(summspell.img, "Flash.png")

    def test_update_image(self):
        summspell = create_summonerspell(300, "SummonerBoost", "Ghost")
        summspell = SummonerSpell.update_img(key=summspell.key, img_fp="Ghost.png")

        self.assertTrue(isinstance(summspell, SummonerSpell))
        self.assertEqual(summspell.key, 300)
        self.assertEqual(summspell.img, "Ghost.png")

    def test_update_desc(self):
        summspell = create_summonerspell(400, "SummonerDot", "Ignite")
        summspell = SummonerSpell.update_desc(key=summspell.key, new_desc="Ignites target enemy.")

        self.assertTrue(isinstance(summspell, SummonerSpell))
        self.assertEqual(summspell.key, 400)
        self.assertEqual(summspell.description, "Ignites target enemy.")

    def test_summoner_spell_to_string(self):
        summspell = create_summonerspell(200, "SummonerBarrier", "Barrier")
        self.assertTrue(isinstance(summspell, SummonerSpell))
        self.assertEqual(str(summspell), summspell.name)
        self.assertEqual(str(summspell), "Barrier")


class SummonerItemModelTest(TestCase):

    def test_create_summoner_item(self):
        summitem = create_summoneritem(3000, "B.F. Sword")
        self.assertTrue(isinstance(summitem, SummonerItem))
        self.assertEqual(summitem.key, 3000)
        self.assertEqual(summitem.name, "B.F. Sword")
        self.assertEqual(summitem.description, "The description")
        self.assertEqual(summitem.plaintext, "The plaintext")
        self.assertEqual(summitem.base_cost, 1300)
        self.assertEqual(summitem.total_cost, 1300)
        self.assertEqual(summitem.img, "B.F. Sword.png")

    def test_update_img(self):
        summitem = create_summoneritem(3100, "Doran's Shield")
        summitem = SummonerItem.update_img(key=summitem.key, new_fp="Doran's Shield.png")

        self.assertTrue(isinstance(summitem, SummonerItem))
        self.assertEqual(summitem.key, 3100)
        self.assertEqual(summitem.img, "Doran's Shield.png")

    def test_update_desc(self):
        summitem = create_summoneritem(3200, "Doran's Blade")
        summitem = SummonerItem.update_desc(key=summitem.key, new_desc="New description")

        self.assertTrue(isinstance(summitem, SummonerItem))
        self.assertEqual(summitem.key, 3200)
        self.assertEqual(summitem.description, "New description")

    def test_update_base_cost(self):
        summitem = create_summoneritem(3300, "Control Ward")
        summitem = SummonerItem.update_base_cost(key=summitem.key, new_cost=50)

        self.assertTrue(isinstance(summitem, SummonerItem))
        self.assertEqual(summitem.key, 3300)
        self.assertEqual(summitem.base_cost, 50)

    def test_update_total_cost(self):
        summitem = create_summoneritem(3500, "Dagger")
        summitem = SummonerItem.update_total_cost(key=summitem.key, new_cost=350)

        self.assertTrue(isinstance(summitem, SummonerItem))
        self.assertEqual(summitem.key, 3500)
        self.assertEqual(summitem.total_cost, 350)

    def test_summoner_item_to_string(self):
        summitem = create_summoneritem(3600, "Crit Cloak")

        self.assertTrue(isinstance(summitem, SummonerItem))
        self.assertEqual(str(summitem), summitem.name)
        self.assertEqual(str(summitem), "Crit Cloak")


class SummonerRuneModelTest(TestCase):

    def test_create_summoner_rune(self):
        summrune = create_summonerrune(8100)
        self.assertTrue(isinstance(summrune, SummonerRune))
        self.assertEqual(summrune.id, 8100)
        self.assertEqual(summrune.name, "Press the Attack")
        self.assertEqual(summrune.img, "PTA.png")
        self.assertEqual(summrune.description, "Hit them 3 times bro")

    def test_update_img(self):
        summrune = create_summonerrune(8200)
        summrune = SummonerRune.update_img(key=summrune.id, new_fp="PTA(2).png")

        self.assertTrue(isinstance(summrune, SummonerRune))
        self.assertEqual(summrune.id, 8200)
        self.assertEqual(summrune.img, "PTA(2).png")

    def test_update_desc(self):
        summrune = create_summonerrune(8300)
        summrune = SummonerRune.update_desc(key=summrune.id, new_desc="New description")

        self.assertTrue(isinstance(summrune, SummonerRune))
        self.assertEqual(summrune.id, 8300)
        self.assertEqual(summrune.description, "New description")

    def test_summoner_rune_to_string(self):
        summrune = create_summonerrune(8400)
        self.assertTrue(isinstance(summrune, SummonerRune))
        self.assertEqual(str(summrune), summrune.name)
        self.assertEqual(str(summrune), "Press the Attack")


class ParticipantModelTest(TestCase):

    def test_create_participant(self):
        match = create_match(5)
        team = create_team(match)
        pchampion = create_champion(20)
        bchampion = create_champion(21)
        summoner = create_summoner("1234", "xx12")
        item = create_summoneritem(134, "Refillable Potion")
        summ_spell0 = create_summonerspell(350, "SummonerHeal", "Heal")
        summ_spell1 = create_summonerspell(450, "SummonerCleanse", "Cleanse")
        p_rune = create_summonerrune(8120)
        s_rune = create_summonerrune(8340)
        participant = create_participant(team, pchampion, bchampion, summoner,
                                         p_rune, s_rune)
        participant.items.add(item)
        participant.spells.add(summ_spell0, summ_spell1)

        self.assertTrue(isinstance(participant, Participant))
        self.assertTrue(isinstance(participant.team, Team))
        self.assertEqual(participant.participant_id, 2)
        self.assertEqual(participant.team, team)
        self.assertEqual(participant.pick_turn, 1)
        self.assertEqual(participant.role, Participant.Role.DUO_SUPPORT)
        self.assertEqual(participant.lane, Participant.Lane.BOTTOM)
        self.assertEqual(participant.pick_id, pchampion)
        self.assertEqual(participant.ban_id, bchampion)
        self.assertEqual(participant.summoner_id, summoner)
        self.assertEqual(participant.rank, Rank.DIAMOND)
        self.assertEqual(participant.tier, Tier.FOUR)
        self.assertEqual(participant.level, 1)
        self.assertEqual(participant.kills, 0)
        self.assertEqual(participant.deaths, 0)
        self.assertEqual(participant.assists, 10)
        self.assertEqual(participant.items.get(pk=item.key), item)
        self.assertEqual(participant.spells.get(pk=summ_spell0.key), summ_spell0)
        self.assertEqual(participant.spells.get(pk=summ_spell1.key), summ_spell1)
        self.assertEqual(participant.primary_rune, p_rune)
        self.assertEqual(participant.secondary_rune, s_rune)
        self.assertEqual(participant.minions_killed, 20)

    def test_clean_model(self):
        match = create_match(6)
        team = create_team(match)
        pchampion = create_champion(22)
        bchampion = create_champion(23)
        summoner = create_summoner("1224", "xx122")
        item = create_summoneritem(137, "Health Potion")
        summ_spell0 = create_summonerspell(650, "SummonerClarity", "Clarity")
        summ_spell1 = create_summonerspell(750, "SummonerSPell", "Spell")
        p_rune = create_summonerrune(8122)
        s_rune = create_summonerrune(8342)
        participant = create_participant(team, pchampion, bchampion, summoner,
                                         p_rune, s_rune)
        participant.items.add(item)
        participant.spells.add(summ_spell0, summ_spell1)

        participant.rank = Rank.CHALLENGER
        participant.save()
        self.assertEqual(participant.rank, Rank.CHALLENGER)
        self.assertEqual(participant.tier, Tier.NOCHOICE)

        participant.secondary_rune = p_rune
        with self.assertRaises(ValidationError):
            participant.save()

        participant.pick_id = bchampion
        with self.assertRaises(ValidationError):
            participant.save()

    def test_participant_to_string(self):
        match = create_match(10)
        team = create_team(match)
        pchampion = create_champion(30)
        bchampion = create_champion(31)
        summoner = create_summoner("1324", "xx132")
        item = create_summoneritem(1310, "Lost Chapter")
        summ_spell0 = create_summonerspell(850, "SummonerSpellThirty", "SpellThirty")
        summ_spell1 = create_summonerspell(950, "SummonerSpellTwenty", "SpellTwenty")
        p_rune = create_summonerrune(9122)
        s_rune = create_summonerrune(9342)
        participant = create_participant(team, pchampion, bchampion, summoner,
                                         p_rune, s_rune)
        participant.items.add(item)
        participant.spells.add(summ_spell0, summ_spell1)

        self.assertTrue(isinstance(participant, Participant))
        self.assertEqual(str(participant), participant.summoner_id.name)
        self.assertEqual(str(participant), "Big AD")


def create_match(key):
    return Match.objects.create(match_id=key, platform_id=Platform.NORTH_AMERICA, game_creation="2020-09-12",
                                queue_id=Queue.RANKED_SOLO_5v5, season=13, average_rank=Rank.DIAMOND,
                                average_tier=Tier.THREE, total_time=1440)


def create_team(match):
    return Team.objects.create(match=match, side=Team.Side.BLUE, win_or_lose="Lose")


def create_champion(key):
    return Champion.objects.create(key=key, champ_id="Annie", name="Annie", img="Annie.png")


def create_summoner(summ_id, acc_id):
    return Summoner.objects.create(summoner_id=summ_id, acc_id=acc_id, name="Big AD",
                                   platform_id=Platform.NORTH_AMERICA,
                                   total_matches=1000, rank=Rank.DIAMOND, tier=Tier.FOUR, league_points=0)


def create_summonerspell(_key, _id, _name):
    return SummonerSpell.objects.create(key=_key, id=_id, name=_name,
                                        description="Teleports your champion a short distance.", img="Flash.png")


def create_summoneritem(_key, _name):
    return SummonerItem.objects.create(key=_key, name=_name, description="The description", plaintext="The plaintext",
                                       base_cost=1300, total_cost=1300, img="B.F. Sword.png")


def create_summonerrune(_id):
    return SummonerRune.objects.create(id=_id, name="Press the Attack", img="PTA.png",
                                       description="Hit them 3 times bro")


def create_participant(_team, champ_pick, champ_ban, summ_id, primary_rune_id,
                       secondary_rune_id):
    return Participant.objects.create(team=_team, pick_turn=1, role=Participant.Role.DUO_SUPPORT,
                                      lane=Participant.Lane.BOTTOM, pick_id=champ_pick, ban_id=champ_ban,
                                      summoner_id=summ_id, rank=Rank.DIAMOND, tier=Tier.FOUR, level=1, kills=0,
                                      deaths=0, assists=10, primary_rune=primary_rune_id,
                                      secondary_rune=secondary_rune_id, minions_killed=20)
