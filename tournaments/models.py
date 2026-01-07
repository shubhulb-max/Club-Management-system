from django.db import models
from players.models import Player

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name

class TournamentParticipation(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='tournament_participations')
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='participants')

    class Meta:
        unique_together = ('player', 'tournament')

    def __str__(self):
        return f"{self.player} is participating in {self.tournament}"
