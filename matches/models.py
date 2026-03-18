from decimal import Decimal

from django.db import models
from teams.models import Team
from grounds.models import Ground
from players.models import Player
from tournaments.models import Tournament

class Match(models.Model):
    STATUS_CHOICES = [
        ("scheduled", "Scheduled"),
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]
    MATCH_TYPE_CHOICES = [
        ("friendly", "Friendly"),
        ("tournament", "Tournament"),
    ]
    MATCH_FORMAT_CHOICES = [
        ("t10", "T10"),
        ("t20", "T20"),
        ("odi", "ODI"),
        ("test", "Test"),
        ("other", "Other"),
    ]
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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="scheduled")
    match_type = models.CharField(max_length=20, choices=MATCH_TYPE_CHOICES, default="friendly")
    tournament = models.ForeignKey(Tournament, on_delete=models.SET_NULL, null=True, blank=True, related_name="matches")
    date = models.DateTimeField()
    match_format = models.CharField(max_length=20, choices=MATCH_FORMAT_CHOICES, null=True, blank=True)
    overs_per_side = models.PositiveSmallIntegerField(null=True, blank=True)
    ball_type = models.CharField(max_length=20, choices=BALL_TYPE_CHOICES, null=True, blank=True)
    team_dress = models.CharField(max_length=100, null=True, blank=True)
    reporting_time = models.TimeField(null=True, blank=True)
    team1_runs = models.PositiveIntegerField(null=True, blank=True)
    team1_wickets = models.PositiveSmallIntegerField(null=True, blank=True)
    team1_overs = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    team2_runs = models.PositiveIntegerField(null=True, blank=True)
    team2_wickets = models.PositiveSmallIntegerField(null=True, blank=True)
    team2_overs = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
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

    @staticmethod
    def overs_to_balls(overs):
        if overs is None:
            return None
        overs = Decimal(str(overs))
        complete_overs = int(overs)
        balls = int((overs - complete_overs) * 10)
        return (complete_overs * 6) + balls

    def get_regulation_overs(self):
        if self.overs_per_side:
            return self.overs_per_side
        return {
            "t10": 10,
            "t20": 20,
            "odi": 50,
        }.get(self.match_format)

    def get_result_summary(self):
        if not self.result:
            return ""
        if self.result == "draw":
            return "Match drawn"
        if self.result == "no_result":
            return "No result"

        opponent_name = self.team2.name if self.team2_id else self.external_opponent
        winner_name = self.team1.name if self.result == "win" else opponent_name
        if not winner_name:
            return ""

        if self.team1_runs is None or self.team2_runs is None:
            return f"{winner_name} won"

        if self.result == "win":
            margin = self.team1_runs - self.team2_runs
            return f"{winner_name} won by {margin} runs" if margin > 0 else f"{winner_name} won"

        balls_used = self.overs_to_balls(self.team2_overs)
        regulation_overs = self.get_regulation_overs()
        if balls_used is not None and regulation_overs is not None:
            balls_remaining = max((regulation_overs * 6) - balls_used, 0)
            if balls_remaining > 0:
                unit = "ball" if balls_remaining == 1 else "balls"
                return f"{winner_name} won by {balls_remaining} {unit}"
            return f"{winner_name} won on the final ball"

        return f"{winner_name} won"


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
