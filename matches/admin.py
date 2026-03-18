from django.contrib import admin
from .models import Match

class MatchAdmin(admin.ModelAdmin):
    list_display = (
        'team1', 'team2', 'external_opponent', 'ground', 'date',
        'match_type', 'tournament', 'match_format', 'ball_type', 'reporting_time', 'result', 'result_summary'
    )
    search_fields = ('team1__name', 'team2__name', 'external_opponent', 'ground__name')
    list_filter = ('date', 'match_type', 'tournament', 'result', 'ground', 'ball_type', 'match_format')

    @admin.display(description='Result Summary')
    def result_summary(self, obj):
        return obj.get_result_summary()

admin.site.register(Match, MatchAdmin)
