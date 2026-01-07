from django.test import TestCase
from rest_framework.exceptions import ValidationError
from .models import Match
from .serializers import MatchSerializer
from teams.models import Team
from players.models import Player
from grounds.models import Ground
import datetime

class MatchSerializerTest(TestCase):

    def setUp(self):
        self.captain1 = Player.objects.create(first_name="Captain", last_name="One", age=30, role="all_rounder")
        self.team1 = Team.objects.create(name="Team One", captain=self.captain1)
        self.ground = Ground.objects.create(name="Test Ground", location="Test Location")
        self.match_date = datetime.datetime.now()

    def test_valid_match_with_internal_team(self):
        captain2 = Player.objects.create(first_name="Captain", last_name="Two", age=31, role="batsman")
        team2 = Team.objects.create(name="Team Two", captain=captain2)
        data = {
            'team1': self.team1.id,
            'team2': team2.id,
            'ground': self.ground.id,
            'date': self.match_date
        }
        serializer = MatchSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_valid_match_with_external_opponent(self):
        data = {
            'team1': self.team1.id,
            'external_opponent': "External Team",
            'ground': self.ground.id,
            'date': self.match_date
        }
        serializer = MatchSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_invalid_match_with_both_opponents(self):
        captain2 = Player.objects.create(first_name="Captain", last_name="Three", age=32, role="bowler")
        team2 = Team.objects.create(name="Team Three", captain=captain2)
        data = {
            'team1': self.team1.id,
            'team2': team2.id,
            'external_opponent': "Another External Team",
            'ground': self.ground.id,
            'date': self.match_date
        }
        serializer = MatchSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_invalid_match_with_no_opponent(self):
        data = {
            'team1': self.team1.id,
            'ground': self.ground.id,
            'date': self.match_date
        }
        serializer = MatchSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)
