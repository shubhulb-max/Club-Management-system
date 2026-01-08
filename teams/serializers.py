from rest_framework import serializers
from .models import Team
from players.models import Player
from players.serializers import PlayerSerializer

class TeamSerializer(serializers.ModelSerializer):
    players = serializers.PrimaryKeyRelatedField(many=True, queryset=Player.objects.all(), write_only=True)
    player_details = PlayerSerializer(many=True, read_only=True, source='players')

    class Meta:
        model = Team
        fields = ['id', 'name', 'captain', 'players', 'player_details']
        extra_kwargs = {
            'players': {'write_only': True}
        }
