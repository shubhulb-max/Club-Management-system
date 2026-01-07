from rest_framework import serializers
from .models import Team
from players.serializers import PlayerSerializer

class TeamSerializer(serializers.ModelSerializer):
    players = PlayerSerializer(many=True, read_only=True)

    class Meta:
        model = Team
        fields = ['id', 'name', 'captain', 'players']
