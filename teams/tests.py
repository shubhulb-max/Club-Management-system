from django.test import TestCase
from .models import Team
from players.models import Player

class TeamModelTest(TestCase):

    def setUp(self):
        self.captain = Player.objects.create(first_name="Team", last_name="Captain", age=30, role="all_rounder")
        self.player = Player.objects.create(first_name="Test", last_name="Player", age=28, role="bowler")
        self.team = Team.objects.create(name="Test Team", captain=self.captain)
        self.team.players.add(self.player)

    def test_team_creation(self):
        team = Team.objects.get(name="Test Team")
        self.assertEqual(team.captain.first_name, "Team")
        self.assertEqual(team.players.count(), 1)
        self.assertEqual(team.players.first().first_name, "Test")
        self.assertEqual(str(team), "Test Team")
