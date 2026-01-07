from django.contrib import admin
from .models import Tournament, TournamentParticipation

class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'entry_fee')
    search_fields = ('name',)

class TournamentParticipationAdmin(admin.ModelAdmin):
    list_display = ('player', 'tournament')
    search_fields = ('player__first_name', 'player__last_name', 'tournament__name')

admin.site.register(Tournament, TournamentAdmin)
admin.site.register(TournamentParticipation, TournamentParticipationAdmin)
