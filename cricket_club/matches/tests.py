from django.test import TestCase
from django.core.exceptions import ValidationError
from .models import Match
from teams.models import Team
from players.models import Player
from grounds.models import Ground
import datetime

class MatchModelTest(TestCase):

    def setUp(self):
        self.captain1 = Player.objects.create(first_name="Captain", last_name="One", age=30, role="all_rounder")
        self.team1 = Team.objects.create(name="Team One", captain=self.captain1)
        self.ground = Ground.objects.create(name="Test Ground", location="Test Location")
        self.match_date = datetime.datetime.now()

    def test_match_with_internal_team(self):
        captain2 = Player.objects.create(first_name="Captain", last_name="Two", age=31, role="batsman")
        team2 = Team.objects.create(name="Team Two", captain=captain2)
        match = Match.objects.create(
            team1=self.team1,
            team2=team2,
            ground=self.ground,
            date=self.match_date
        )
        self.assertEqual(str(match), f"Team One vs Team Two on {self.match_date.strftime('%Y-%m-%d')}")

    def test_match_with_external_opponent(self):
        match = Match.objects.create(
            team1=self.team1,
            external_opponent="External Team",
            ground=self.ground,
            date=self.match_date
        )
        self.assertEqual(str(match), f"Team One vs External Team on {self.match_date.strftime('%Y-%m-%d')}")

    def test_validation_error_with_both_opponents(self):
        captain2 = Player.objects.create(first_name="Captain", last_name="Three", age=32, role="bowler")
        team2 = Team.objects.create(name="Team Three", captain=captain2)
        match = Match(
            team1=self.team1,
            team2=team2,
            external_opponent="Another External Team",
            ground=self.ground,
            date=self.match_date
        )
        with self.assertRaises(ValidationError):
            match.clean()

    def test_validation_error_with_no_opponent(self):
        match = Match(
            team1=self.team1,
            ground=self.ground,
            date=self.match_date
        )
        with self.assertRaises(ValidationError):
            match.clean()
