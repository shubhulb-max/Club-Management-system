from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from .models import Match, Lineup, LineupEntry

class MatchSerializer(serializers.ModelSerializer):
    result_summary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Match
        fields = [
            'id', 'team1', 'team2', 'external_opponent', 'ground', 'date',
            'status',
            'match_type', 'tournament',
            'match_format', 'overs_per_side', 'ball_type', 'team_dress', 'reporting_time',
            'team1_runs', 'team1_wickets', 'team1_overs', 'team2_runs', 'team2_wickets', 'team2_overs',
            'result', 'winner', 'result_summary'
        ]
        read_only_fields = ['result', 'winner', 'result_summary']

    def get_result_summary(self, obj):
        return obj.get_result_summary()

    def validate(self, data):
        """
        Check that a match has either a second internal team or an external opponent, but not both.
        """
        instance = self.instance
        team1 = data.get('team1') or getattr(instance, 'team1', None)
        team2 = data.get('team2') if 'team2' in data else getattr(instance, 'team2', None)
        external_opponent = (
            data.get('external_opponent')
            if 'external_opponent' in data else getattr(instance, 'external_opponent', None)
        )
        tournament = data.get('tournament') if 'tournament' in data else getattr(instance, 'tournament', None)
        status = data.get('status') if 'status' in data else getattr(instance, 'status', 'scheduled')
        match_type = data.get('match_type') if 'match_type' in data else getattr(instance, 'match_type', 'friendly')
        if not match_type:
            match_type = 'friendly'
            data['match_type'] = match_type
        match_format = data.get('match_format') if 'match_format' in data else getattr(instance, 'match_format', None)
        team1_runs = data.get('team1_runs') if 'team1_runs' in data else getattr(instance, 'team1_runs', None)
        team1_wickets = data.get('team1_wickets') if 'team1_wickets' in data else getattr(instance, 'team1_wickets', None)
        team2_runs = data.get('team2_runs') if 'team2_runs' in data else getattr(instance, 'team2_runs', None)
        team2_wickets = data.get('team2_wickets') if 'team2_wickets' in data else getattr(instance, 'team2_wickets', None)
        team1_overs = data.get('team1_overs') if 'team1_overs' in data else getattr(instance, 'team1_overs', None)
        team2_overs = data.get('team2_overs') if 'team2_overs' in data else getattr(instance, 'team2_overs', None)
        self._derive_result_from_scores(data, team1, team2, team1_runs, team2_runs)
        team1_runs = data.get('team1_runs') if 'team1_runs' in data else getattr(instance, 'team1_runs', None)
        team2_runs = data.get('team2_runs') if 'team2_runs' in data else getattr(instance, 'team2_runs', None)
        result = data.get('result') if 'result' in data else getattr(instance, 'result', None)
        winner = data.get('winner') if 'winner' in data else getattr(instance, 'winner', None)

        if team2 and external_opponent:
            raise serializers.ValidationError("A match can have a second internal team or an external opponent, but not both.")
        if not team2 and not external_opponent:
            raise serializers.ValidationError("A match must have either a second internal team or an external opponent.")
        if tournament and match_type != 'tournament':
            data['match_type'] = 'tournament'
            match_type = 'tournament'
        if match_type == 'tournament' and tournament is None:
            raise serializers.ValidationError({'tournament': "Tournament is required when match_type is tournament."})
        if match_type == 'friendly' and tournament is not None:
            raise serializers.ValidationError({'tournament': "Friendly matches cannot be linked to a tournament."})
        if self.instance is None:
            missing = [field for field in ('match_format', 'ball_type', 'team_dress') if not data.get(field)]
            if missing:
                raise serializers.ValidationError({field: "This field is required." for field in missing})

        for field_name, overs in (('team1_overs', team1_overs), ('team2_overs', team2_overs)):
            self._validate_overs_format(field_name, overs)

        if team1_wickets is not None and team1_wickets > 10:
            raise serializers.ValidationError({'team1_wickets': "Wickets cannot be more than 10."})
        if team2_wickets is not None and team2_wickets > 10:
            raise serializers.ValidationError({'team2_wickets': "Wickets cannot be more than 10."})

        score_fields = (
            'team1_runs', 'team1_wickets', 'team1_overs',
            'team2_runs', 'team2_wickets', 'team2_overs'
        )
        score_values = [team1_runs, team1_wickets, team1_overs, team2_runs, team2_wickets, team2_overs]
        has_partial_scores = any(value is not None for value in score_values) and any(value is None for value in score_values)
        if has_partial_scores:
            raise serializers.ValidationError({field: "All score and overs fields are required together." for field in score_fields})

        if status == 'completed' and any(value is None for value in score_values):
            raise serializers.ValidationError({'status': "Completed matches require runs, wickets, and overs for both teams."})
        if status in ('scheduled', 'cancelled') and any(value is not None for value in score_values):
            raise serializers.ValidationError({'status': "Scheduled or cancelled matches cannot have result scores."})

        if result == 'win':
            if winner and team1 and winner.id != team1.id:
                raise serializers.ValidationError({'winner': "Winner must be team1 when result is win."})
            if team1_runs is not None and team2_runs is not None and team1_runs <= team2_runs:
                raise serializers.ValidationError({'team1_runs': "team1_runs must be greater than team2_runs for a win."})
        elif result == 'loss':
            if winner and team1 and winner.id == team1.id:
                raise serializers.ValidationError({'winner': "Winner cannot be team1 when result is loss."})
            if team2 and winner and winner.id != team2.id:
                raise serializers.ValidationError({'winner': "Winner must be team2 for internal matches marked as loss."})
            if team1_runs is not None and team2_runs is not None and team2_runs <= team1_runs:
                raise serializers.ValidationError({'team2_runs': "team2_runs must be greater than team1_runs for a loss."})
        elif result in ('draw', 'no_result') and winner is not None:
            raise serializers.ValidationError({'winner': "Winner must be empty when result is draw or no_result."})

        if match_format == 'test' and data.get('overs_per_side') == 0:
            raise serializers.ValidationError({'overs_per_side': "overs_per_side must be greater than 0."})

        return data

    def _validate_overs_format(self, field_name, overs):
        if overs is None:
            return
        overs_string = str(overs)
        if '.' not in overs_string:
            return
        balls = overs_string.split('.', 1)[1]
        if not balls.isdigit() or len(balls) != 1 or int(balls) > 5:
            raise serializers.ValidationError({field_name: "Overs must use cricket notation, for example 17.2 or 20.0."})

    def _derive_result_from_scores(self, data, team1, team2, team1_runs, team2_runs):
        if team1_runs is None or team2_runs is None or team1 is None:
            return
        if team1_runs > team2_runs:
            data['result'] = 'win'
            data['winner'] = team1
        elif team2_runs > team1_runs:
            data['result'] = 'loss'
            if team2 is not None:
                data['winner'] = team2
            else:
                data['winner'] = None
        else:
            data['result'] = 'draw'
            data['winner'] = None


class LineupEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = LineupEntry
        fields = [
            "id",
            "player",
            "batting_order",
            "role",
            "is_captain",
            "is_wicket_keeper",
            "is_substitute",
            "extra_data",
        ]
        read_only_fields = ["id"]


class LineupSerializer(serializers.ModelSerializer):
    entries = LineupEntrySerializer(many=True)

    class Meta:
        model = Lineup
        fields = [
            "id",
            "match",
            "team",
            "created_by",
            "created_at",
            "updated_at",
            "entries",
        ]
        read_only_fields = ["id", "created_by", "created_at", "updated_at"]

    def _ensure_captain(self, team, user):
        player = getattr(user, "player", None)
        if not player:
            raise PermissionDenied("Only players can manage lineups.")
        if team.captain_id != player.id:
            raise PermissionDenied("Only the team captain can manage this lineup.")
        return player

    def validate(self, attrs):
        match = attrs.get("match") or getattr(self.instance, "match", None)
        team = attrs.get("team") or getattr(self.instance, "team", None)

        if not match or not team:
            raise serializers.ValidationError("Match and team are required.")

        request = self.context.get("request")
        if request and request.user:
            self._ensure_captain(team, request.user)

        if team.id not in {match.team1_id, match.team2_id}:
            raise serializers.ValidationError("Team does not belong to this match.")

        entries = attrs.get("entries", None)
        if self.instance is None and not entries:
            raise serializers.ValidationError({"entries": "Lineup entries are required."})

        if entries is not None:
            if len(entries) > 11:
                raise serializers.ValidationError({"entries": "Lineup cannot exceed 11 players."})

            player_ids = [entry["player"].id for entry in entries]
            if len(set(player_ids)) != len(player_ids):
                raise serializers.ValidationError({"entries": "Players must be unique in the lineup."})

            team_player_ids = set(team.players.values_list("id", flat=True))
            for player_id in player_ids:
                if player_id not in team_player_ids:
                    raise serializers.ValidationError({"entries": "All players must belong to the team."})

            batting_orders = [entry["batting_order"] for entry in entries]
            if len(set(batting_orders)) != len(batting_orders):
                raise serializers.ValidationError({"entries": "Batting order values must be unique."})
            for order in batting_orders:
                if order < 1 or order > 11:
                    raise serializers.ValidationError({"entries": "Batting order must be between 1 and 11."})

            captains = [entry for entry in entries if entry.get("is_captain")]
            if len(captains) > 1:
                raise serializers.ValidationError({"entries": "Only one captain can be set in the lineup."})

        return attrs

    def create(self, validated_data):
        entries_data = validated_data.pop("entries", [])
        request = self.context.get("request")
        created_by = None
        if request and request.user:
            created_by = self._ensure_captain(validated_data["team"], request.user)

        with transaction.atomic():
            lineup = Lineup.objects.create(created_by=created_by, **validated_data)
            self._save_entries(lineup, entries_data)
        return lineup

    def update(self, instance, validated_data):
        entries_data = validated_data.pop("entries", None)

        if "match" in validated_data and validated_data["match"].id != instance.match_id:
            raise serializers.ValidationError({"match": "Match cannot be changed for an existing lineup."})
        if "team" in validated_data and validated_data["team"].id != instance.team_id:
            raise serializers.ValidationError({"team": "Team cannot be changed for an existing lineup."})

        with transaction.atomic():
            if entries_data is not None:
                instance.entries.all().delete()
                self._save_entries(instance, entries_data)
                instance.save(update_fields=["updated_at"])
        return instance

    def _save_entries(self, lineup, entries_data):
        LineupEntry.objects.bulk_create(
            [LineupEntry(lineup=lineup, **entry) for entry in entries_data]
        )
