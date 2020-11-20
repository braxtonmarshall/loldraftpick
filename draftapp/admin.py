from django.contrib import admin
from .models import *

admin.site.register(Match)
admin.site.register(Team)
admin.site.register(Champion)
admin.site.register(Summoner)
admin.site.register(Participant)
admin.site.register(SummonerSpell)
admin.site.register(SummonerRune)
admin.site.register(SummonerItem)
admin.site.register(ParticipantSummonerSpell)
admin.site.register(ParticipantSummonerItems)
