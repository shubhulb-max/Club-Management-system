from django.db import models
from players.models import Player

class Team(models.Model):
    name = models.CharField(max_length=100)
    captain = models.ForeignKey(Player, on_delete=models.SET_NULL, null=True, related_name='captain_of')
    players = models.ManyToManyField(Player, related_name='teams')
    logo = models.ImageField(upload_to='team_logos/', null=True, blank=True)

    def __str__(self):
        return self.name
