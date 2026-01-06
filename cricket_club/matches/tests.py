from django.test import TestCase
from .models import Match
from teams.models import Team
from players.models import Player
import datetime

class MatchModelTest(TestCase):

    def setUp(self):
        captain1 = Player.objects.create(first_name="Captain", last_name="One", age=30, role="all_rounder")
        captain2 = Player.objects.create(first_name="Captain", last_name="Two", age=31, role="batsman")
        self.team1 = Team.objects.create(name="Team One", captain=captain1)
        self.team2 = Team.objects.create(name="Team Two", captain=captain2)
        self.match_date = datetime.datetime.now()
        self.match = Match.objects.create(
            team1=self.team1,
            team2=self.team2,
            venue="Test Venue",
            date=self.match_date,
            result="win",
            winner=self.team1
        )

    def test_match_creation(self):
        match = Match.objects.get(venue="Test Venue")
        self.assertEqual(match.team1.name, "Team One")
        self.assertEqual(match.team2.name, "Team Two")
        self.assertEqual(match.result, "win")
        self.assertEqual(match.winner.name, "Team One")
        self.assertEqual(str(match), f"Team One vs Team Two on {self.match_date.strftime('%Y-%m-%d')}")
