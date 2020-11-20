from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now


class Platform(models.TextChoices):
    BRAZIL = 'BR1'
    EUROPE_NORTH = 'EUN1'
    EUROPE_WEST = 'EUW1'
    JAPAN = 'JP1'
    KR = 'KR'
    LATIN_AMERICA_ONE = 'LA1'
    LATIN_AMERICA_TWO = 'LA2'
    NORTH_AMERICA = 'NA1'
    OCEANIC = 'OC1'
    TURKEY = 'TR1'
    RUSSIA = 'RU'


class Queue(models.IntegerChoices):
    NORMAL_DRAFT_PICK_5v5 = 400
    RANKED_SOLO_5v5 = 420
    RANKED_FLEX_5v5 = 440
    ARAM_5v5 = 450


class Rank(models.TextChoices):
    CHALLENGER = 'CHR', _('Challenger')
    GRANDMASTER = 'GMR', _('Grandmaster')
    MASTER = 'MR', _('Master')
    DIAMOND = 'DMD', _('Diamond')
    PLATINUM = 'PLAT', _('Platinum')
    GOLD = 'GLD', _('Gold')
    SILVER = 'SVR', _('Silver')
    BRONZE = 'BRZ', _('Bronze')
    IRON = 'IRON', _('Iron')
    UNRANKED = 'UNRK', _('Unranked')


class Tier(models.TextChoices):
    ONE = 'I', _('I')
    TWO = 'II', _('II')
    THREE = 'III', _('III')
    FOUR = 'IV', _('IV')
    NOCHOICE = '', _('')


class Role(models.TextChoices):
    DUO = 'DUO'
    NONE = 'NONE'
    SOLO = 'SOLO'
    DUO_CARRY = 'CARRY'
    DUO_SUPPORT = 'SUPPORT'


class Lane(models.TextChoices):
    TOP = 'TOP'
    JUNGLE = 'JG'
    MIDDLE = 'MID'
    BOTTOM = 'BOT'


class Match(models.Model):
    match_id = models.BigIntegerField(primary_key=True)
    platform_id = models.CharField(max_length=4, choices=Platform.choices)
    game_creation = models.DateTimeField()
    queue_id = models.PositiveSmallIntegerField(choices=Queue.choices)
    season = models.SmallIntegerField(validators=[MaxValueValidator(13), MinValueValidator(1)])
    average_rank = models.CharField(max_length=4, choices=Rank.choices)
    average_tier = models.CharField(max_length=3, choices=Tier.choices, null=True, blank=True)
    total_time = models.PositiveSmallIntegerField()

    def __str__(self):
        return str(self.match_id)

    def clean_model(self) -> None:
        if self.average_rank in ['CHR', 'GMR', 'MR']:
            self.average_tier = Tier.NOCHOICE

    def save(self, *args, **kwargs):
        self.clean_model()
        super().save(*args, **kwargs)

    @classmethod
    def update_avg_rank(cls, match_id, new_rank):
        with transaction.atomic():
            match = (cls.objects.select_for_update().get(match_id=match_id))
            match.average_rank = new_rank
            match.save()
        return match

    @classmethod
    def update_avg_tier(cls, match_id, new_tier):
        with transaction.atomic():
            match = (cls.objects.select_for_update().get(match_id=match_id))
            match.average_tier = new_tier
            match.save()
        return match


class Team(models.Model):
    class Side(models.IntegerChoices):
        BLUE = 100
        RED = 200

    team_id = models.AutoField(primary_key=True)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    side = models.PositiveSmallIntegerField(choices=Side.choices)
    win_or_lose = models.CharField(max_length=4)

    def __str__(self):
        return str(self.team_id)


class Champion(models.Model):
    key = models.SmallIntegerField(unique=True)
    champ_id = models.CharField(max_length=15)
    name = models.CharField(max_length=15)
    img = models.FilePathField(path='/home/mars/Workspace/Python/Loldraft.gg/draftapp/static/img/champion')

    def __str__(self):
        return self.name


class Summoner(models.Model):
    summoner_id = models.CharField(max_length=100, primary_key=True)
    acc_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=16)
    platform_id = models.CharField(max_length=4, choices=Platform.choices)
    last_update = models.DateTimeField(default=now, editable=True)
    total_matches = models.PositiveSmallIntegerField()
    rank = models.CharField(max_length=4, choices=Rank.choices)
    tier = models.CharField(max_length=3, choices=Tier.choices, null=True)
    league_points = models.SmallIntegerField(validators=[MaxValueValidator(100), MinValueValidator(0)])

    def __str__(self):
        return self.name

    def clean_model(self) -> None:
        if self.rank in ['CHR', 'GMR', 'MR']:
            self.tier = Tier.NOCHOICE

    def save(self, *args, **kwargs):
        self.clean_model()
        super().save(*args, **kwargs)

    @classmethod
    def update_name(cls, summ_id, new_name):
        with transaction.atomic():
            summoner = (cls.objects.select_for_update().get(summoner_id=summ_id))

            summoner.name = new_name
            summoner.save()
        return summoner

    @classmethod
    def update_total_matches(cls, summ_id, matches):
        with transaction.atomic():
            summoner = (cls.objects.select_for_update().get(summoner_id=summ_id))

            summoner.total_matches = matches
            summoner.save()
        return summoner

    @classmethod
    def update_rank(cls, summ_id, new_rank):
        with transaction.atomic():
            summoner = (cls.objects.select_for_update().get(summoner_id=summ_id))

            summoner.rank = Rank[new_rank]
            summoner.save()
        return summoner

    @classmethod
    def update_tier(cls, summ_id, new_tier):
        with transaction.atomic():
            summoner = (cls.objects.select_for_update().get(summoner_id=summ_id))

            summoner.tier = Tier[new_tier]
            summoner.save()
        return summoner

    @classmethod
    def update_league_points(cls, summ_id, new_points):
        with transaction.atomic():
            summoner = (cls.objects.select_for_update().get(summoner_id=summ_id))

            summoner.league_points = new_points
            summoner.save()
        return summoner

    @classmethod
    def update_last_update(cls, summ_id, update):
        # TODO
        return


class SummonerSpell(models.Model):
    key = models.SmallIntegerField(primary_key=True)
    id = models.CharField(max_length=32, unique=True)
    name = models.CharField(max_length=12)
    description = models.TextField()
    img = models.FilePathField(path='/home/mars/Workspace/Python/Loldraft.gg/draftapp/static/img/spells')

    def __str__(self):
        return self.name

    @classmethod
    def update_img(cls, key, img_fp):
        with transaction.atomic():
            summoner_spell = (cls.objects.select_for_update().get(key=key))

            summoner_spell.img = img_fp
            summoner_spell.save()
        return summoner_spell

    @classmethod
    def update_desc(cls, key, new_desc):
        with transaction.atomic():
            summoner_spell = (cls.objects.select_for_update().get(key=key))

            summoner_spell.description = new_desc
            summoner_spell.save()
        return summoner_spell


class SummonerItem(models.Model):
    key = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    plaintext = models.TextField()
    base_cost = models.PositiveSmallIntegerField(validators=[MaxValueValidator(0), MinValueValidator(4000)])
    total_cost = models.PositiveSmallIntegerField(validators=[MaxValueValidator(0), MinValueValidator(4000)])
    img = models.FilePathField(path='/home/mars/Workspace/Python/Loldraft.gg/draftapp/static/img/items')

    def __str__(self):
        return self.name

    @classmethod
    def update_img(cls, key, new_fp):
        with transaction.atomic():
            summoner_item = (cls.objects.select_for_update().get(key=key))

            summoner_item.img = new_fp
            summoner_item.save()
        return summoner_item

    @classmethod
    def update_desc(cls, key, new_desc):
        with transaction.atomic():
            summoner_item = (cls.objects.select_for_update().get(key=key))

            summoner_item.description = new_desc
            summoner_item.save()
        return summoner_item

    @classmethod
    def update_base_cost(cls, key, new_cost):
        with transaction.atomic():
            summoner_item = (cls.objects.select_for_update().get(key=key))

            summoner_item.base_cost = new_cost
            summoner_item.save()
        return summoner_item

    @classmethod
    def update_total_cost(cls, key, new_cost):
        with transaction.atomic():
            summoner_item = (cls.objects.select_for_update().get(key=key))

            summoner_item.total_cost = new_cost
            summoner_item.save()
        return summoner_item


class SummonerRune(models.Model):
    id = models.SmallIntegerField(primary_key=True)
    name = models.CharField(max_length=32)
    img = models.FilePathField(path='/home/mars/Workspace/Python/Loldraft.gg/draftapp/static/img/runes')
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name

    @classmethod
    def update_img(cls, key, new_fp):
        with transaction.atomic():
            summoner_rune = (cls.objects.select_for_update().get(id=key))

            summoner_rune.img = new_fp
            summoner_rune.save()
        return summoner_rune

    @classmethod
    def update_desc(cls, key, new_desc):
        with transaction.atomic():
            summoner_rune = (cls.objects.select_for_update().get(id=key))

            summoner_rune.description = new_desc
            summoner_rune.save()
        return summoner_rune


class Participant(models.Model):
    participant_id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    pick_turn = models.SmallIntegerField(validators=[MaxValueValidator(10), MinValueValidator(1)])
    role = models.CharField(max_length=11, choices=Role.choices)
    lane = models.CharField(max_length=6, choices=Lane.choices)
    pick_id = models.ForeignKey(Champion, to_field="key", on_delete=models.PROTECT, related_name='related_pick')
    ban_id = models.ForeignKey(Champion, to_field="key", on_delete=models.PROTECT, related_name='related_ban',
                               null=True, blank=True)
    summoner_id = models.ForeignKey(Summoner, on_delete=models.PROTECT)
    rank = models.CharField(max_length=4, choices=Rank.choices)
    tier = models.CharField(max_length=3, choices=Tier.choices, null=True)
    level = models.SmallIntegerField(validators=[MaxValueValidator(18), MinValueValidator(1)])
    kills = models.PositiveSmallIntegerField()
    deaths = models.PositiveSmallIntegerField()
    assists = models.PositiveSmallIntegerField()
    items = models.ManyToManyField(SummonerItem, through='ParticipantSummonerItems')
    spells = models.ManyToManyField(SummonerSpell, through='ParticipantSummonerSpell')
    primary_rune = models.ForeignKey(SummonerRune, on_delete=models.PROTECT, related_name='primary_rune', null=True,
                                     blank=True)
    secondary_rune = models.ForeignKey(SummonerRune, on_delete=models.PROTECT, related_name='secondary_rune', null=True,
                                       blank=True)
    minions_killed = models.PositiveSmallIntegerField()

    @classmethod
    def update_lane(cls, par_id, new_lane):
        with transaction.atomic():
            participant = (cls.objects.select_for_update().get(participant_id=par_id))

            participant.lane = Lane[new_lane]
            participant.save()
        return participant

    @classmethod
    def update_role(cls, par_id, new_role):
        with transaction.atomic():
            participant = (cls.objects.select_for_update().get(participant_id=par_id))

            participant.role = Role[new_role]
            participant.save()
        return participant

    def __str__(self):
        return str(self.summoner_id.name)

    def clean_model(self):

        # Masters+ don't have tiers
        if self.rank in ['CHR', 'GMR', 'MR']:
            self.tier = Tier.NOCHOICE

        # Primary rune != Secondary Rune
        if self.primary_rune == self.secondary_rune:
            raise ValidationError('Primary rune cannot be the same as the secondary rune.')

        # Can't pick a banned champion!
        if self.pick_id == self.ban_id:
            raise ValidationError('Cannot pick a champion that is banned!')

    def save(self, *args, **kwargs):
        self.clean_model()
        super().save(*args, **kwargs)


class ParticipantSummonerSpell(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    summoner_spell = models.ForeignKey(SummonerSpell, on_delete=models.PROTECT)

    class Meta:
        unique_together = ('participant', 'summoner_spell')


class ParticipantSummonerItems(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    item = models.ForeignKey(SummonerItem, on_delete=models.PROTECT)
    amount = models.SmallIntegerField(default=1, validators=[MaxValueValidator(6)])

    class Meta:
        unique_together = ('participant', 'item', 'amount')
