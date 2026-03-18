from django.test import TestCase
from rest_framework.exceptions import ValidationError
from .models import Match
from .serializers import MatchSerializer
from teams.models import Team
from players.models import Player
from grounds.models import Ground
from tournaments.models import Tournament
import datetime

class MatchSerializerTest(TestCase):

    def setUp(self):
        self.captain1 = Player.objects.create(first_name="Captain", last_name="One", age=30, role="all_rounder")
        self.team1 = Team.objects.create(name="Team One", captain=self.captain1)
        self.ground = Ground.objects.create(name="Test Ground", location="Test Location")
        self.match_date = datetime.datetime.now()
        self.base_data = {
            'team1': self.team1.id,
            'ground': self.ground.id,
            'date': self.match_date,
            'status': 'scheduled',
            'match_type': 'friendly',
            'match_format': 't20',
            'ball_type': 'tennis',
            'team_dress': 'Blue',
            'reporting_time': datetime.time(9, 0),
        }

    def test_valid_match_with_internal_team(self):
        captain2 = Player.objects.create(first_name="Captain", last_name="Two", age=31, role="batsman")
        team2 = Team.objects.create(name="Team Two", captain=captain2)
        data = {
            **self.base_data,
            'team2': team2.id,
        }
        serializer = MatchSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_valid_match_with_external_opponent(self):
        data = {
            **self.base_data,
            'external_opponent': "External Team",
        }
        serializer = MatchSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))

    def test_tournament_match_requires_tournament(self):
        data = {
            **self.base_data,
            'match_type': 'tournament',
            'external_opponent': "External Team",
        }
        serializer = MatchSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_tournament_field_sets_match_type(self):
        tournament = Tournament.objects.create(
            name="Summer Cup",
            start_date=self.match_date.date(),
            entry_fee="1000.00",
        )
        data = {
            **self.base_data,
            'external_opponent': "External Team",
            'match_type': 'friendly',
            'tournament': tournament.id,
        }
        serializer = MatchSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertEqual(serializer.validated_data['match_type'], 'tournament')
        self.assertEqual(serializer.validated_data['tournament'], tournament)

    def test_invalid_match_with_both_opponents(self):
        captain2 = Player.objects.create(first_name="Captain", last_name="Three", age=32, role="bowler")
        team2 = Team.objects.create(name="Team Three", captain=captain2)
        data = {
            **self.base_data,
            'team2': team2.id,
            'external_opponent': "Another External Team",
        }
        serializer = MatchSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_invalid_match_with_no_opponent(self):
        data = dict(self.base_data)
        serializer = MatchSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_invalid_match_without_match_format(self):
        data = {
            key: value for key, value in self.base_data.items() if key != 'match_format'
        }
        data['external_opponent'] = "External Team"
        serializer = MatchSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_partial_scores_are_rejected(self):
        data = {
            **self.base_data,
            'external_opponent': "External Team",
            'team1_runs': 180,
            'team1_overs': '20.0',
        }
        serializer = MatchSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_completed_match_requires_full_scores(self):
        data = {
            **self.base_data,
            'status': 'completed',
            'external_opponent': "External Team",
        }
        serializer = MatchSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_scheduled_match_cannot_have_scores(self):
        data = {
            **self.base_data,
            'external_opponent': "External Team",
            'team1_runs': 175,
            'team1_wickets': 6,
            'team1_overs': '20.0',
            'team2_runs': 107,
            'team2_wickets': 10,
            'team2_overs': '15.3',
        }
        serializer = MatchSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_separate_score_fields_derive_result(self):
        captain2 = Player.objects.create(first_name="Captain", last_name="Five", age=28, role="bowler")
        team2 = Team.objects.create(name="Team Five", captain=captain2)
        data = {
            **self.base_data,
            'status': 'completed',
            'team2': team2.id,
            'team1_runs': 175,
            'team1_wickets': 6,
            'team1_overs': '20.0',
            'team2_runs': 107,
            'team2_wickets': 10,
            'team2_overs': '15.3',
        }
        serializer = MatchSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertEqual(serializer.validated_data['team1_runs'], 175)
        self.assertEqual(serializer.validated_data['team1_wickets'], 6)
        self.assertEqual(str(serializer.validated_data['team1_overs']), '20.0')
        self.assertEqual(serializer.validated_data['team2_runs'], 107)
        self.assertEqual(serializer.validated_data['team2_wickets'], 10)
        self.assertEqual(str(serializer.validated_data['team2_overs']), '15.3')
        self.assertEqual(serializer.validated_data['result'], 'win')
        self.assertEqual(serializer.validated_data['winner'], self.team1)

    def test_manual_result_and_winner_are_ignored(self):
        captain2 = Player.objects.create(first_name="Captain", last_name="Six", age=27, role="batsman")
        team2 = Team.objects.create(name="Team Six", captain=captain2)
        data = {
            **self.base_data,
            'status': 'completed',
            'team2': team2.id,
            'team1_runs': 175,
            'team1_wickets': 6,
            'team1_overs': '20.0',
            'team2_runs': 107,
            'team2_wickets': 10,
            'team2_overs': '15.3',
            'result': 'loss',
            'winner': team2.id,
        }
        serializer = MatchSerializer(data=data)
        self.assertTrue(serializer.is_valid(raise_exception=True))
        self.assertEqual(serializer.validated_data['result'], 'win')
        self.assertEqual(serializer.validated_data['winner'], self.team1)

    def test_result_summary_uses_run_margin(self):
        match = Match.objects.create(
            team1=self.team1,
            external_opponent="External Team",
            ground=self.ground,
            date=self.match_date,
            match_format='t20',
            ball_type='tennis',
            team_dress='Blue',
            reporting_time=datetime.time(9, 0),
            result='win',
            winner=self.team1,
            team1_runs=180,
            team1_wickets=6,
            team1_overs='20.0',
            team2_runs=160,
            team2_wickets=10,
            team2_overs='19.4',
        )
        serializer = MatchSerializer(instance=match)
        self.assertEqual(serializer.data['result_summary'], 'Team One won by 20 runs')

    def test_result_summary_uses_ball_margin(self):
        captain2 = Player.objects.create(first_name="Captain", last_name="Four", age=29, role="bowler")
        team2 = Team.objects.create(name="Team Four", captain=captain2)
        match = Match.objects.create(
            team1=self.team1,
            team2=team2,
            ground=self.ground,
            date=self.match_date,
            match_format='t20',
            ball_type='tennis',
            team_dress='Blue',
            reporting_time=datetime.time(9, 0),
            result='loss',
            winner=team2,
            team1_runs=150,
            team1_wickets=10,
            team1_overs='20.0',
            team2_runs=151,
            team2_wickets=6,
            team2_overs='18.4',
        )
        serializer = MatchSerializer(instance=match)
        self.assertEqual(serializer.data['result_summary'], 'Team Four won by 8 balls')
