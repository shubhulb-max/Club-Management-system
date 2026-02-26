from django.db import models
from teams.models import Team
from grounds.models import Ground
from players.models import Player

class Match(models.Model):
    BALL_TYPE_CHOICES = [
        ("whiteleather", "RedLeather"),
        ("redleather", "WhiteLeather"),
        ("pinkleather", "PinkLeather"),
        ("tennis", "Tennis"),
        ("other", "Other"),
    ]
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team1')
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='matches_as_team2', null=True, blank=True)
    external_opponent = models.CharField(max_length=100, null=True, blank=True)
    ground = models.ForeignKey(Ground, on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField()
    ball_type = models.CharField(max_length=20, choices=BALL_TYPE_CHOICES, null=True, blank=True)
    team_dress = models.CharField(max_length=100, null=True, blank=True)
    reporting_time = models.TimeField(null=True, blank=True)
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


class Lineup(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name="lineups")
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name="lineups")
    created_by = models.ForeignKey(
        Player, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_lineups"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("match", "team")

    def __str__(self):
        return f"{self.team} lineup for {self.match}"


class LineupEntry(models.Model):
    lineup = models.ForeignKey(Lineup, on_delete=models.CASCADE, related_name="entries")
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name="lineup_entries")
    batting_order = models.PositiveSmallIntegerField()
    role = models.CharField(max_length=30)
    is_captain = models.BooleanField(default=False)
    is_wicket_keeper = models.BooleanField(default=False)
    is_substitute = models.BooleanField(default=False)
    extra_data = models.JSONField(default=dict, blank=True)

    class Meta:
        unique_together = (
            ("lineup", "player"),
            ("lineup", "batting_order"),
        )

    def __str__(self):
        return f"{self.player} ({self.lineup.team})"
