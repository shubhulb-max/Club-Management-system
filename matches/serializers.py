from rest_framework import serializers
from .models import Match

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
