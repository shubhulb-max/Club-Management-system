from django.db import models
from teams.models import Team
from grounds.models import Ground

class Match(models.Model):
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team2', null=True, blank=True)
    external_opponent = models.CharField(max_length=100, null=True, blank=True)
    ground = models.ForeignKey(Ground, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField()
    RESULT_CHOICES = [
        ('win', 'Win'),
        ('loss', 'Loss'),
        ('draw', 'Draw'),
        ('no_result', 'No Result'),
    ]
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, blank=True, null=True)
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='won_matches')

    def __str__(self):
        opponent = self.team2 if self.team2 else self.external_opponent
        return f"{self.team1} vs {opponent} on {self.date.strftime('%Y-%m-%d')}"
