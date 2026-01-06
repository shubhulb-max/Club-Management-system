from django.db import models
from teams.models import Team

class Match(models.Model):
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team2')
    venue = models.CharField(max_length=100)
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
        return f"{self.team1} vs {self.team2} on {self.date.strftime('%Y-%m-%d')}"
