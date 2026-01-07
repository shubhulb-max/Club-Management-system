from django.contrib import admin
from .models import Match

class MatchAdmin(admin.ModelAdmin):
    list_display = ('team1', 'team2', 'external_opponent', 'ground', 'date', 'result')
    search_fields = ('team1__name', 'team2__name', 'external_opponent', 'ground__name')
    list_filter = ('date', 'result', 'ground')

admin.site.register(Match, MatchAdmin)
