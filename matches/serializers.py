from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied
from .models import Match, Lineup, LineupEntry

class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = [
            'id', 'team1', 'team2', 'external_opponent', 'ground', 'date',
            'ball_type', 'team_dress', 'reporting_time', 'result', 'winner'
        ]

    def validate(self, data):
        """
        Check that a match has either a second internal team or an external opponent, but not both.
        """
        if data.get('team2') and data.get('external_opponent'):
            raise serializers.ValidationError("A match can have a second internal team or an external opponent, but not both.")
        if not data.get('team2') and not data.get('external_opponent'):
            raise serializers.ValidationError("A match must have either a second internal team or an external opponent.")
        if self.instance is None:
            missing = [field for field in ('ball_type', 'team_dress', 'reporting_time') if not data.get(field)]
            if missing:
                raise serializers.ValidationError({field: "This field is required." for field in missing})
        return data


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
