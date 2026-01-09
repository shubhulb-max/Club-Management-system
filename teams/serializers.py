from rest_framework import serializers
from players.serializers import PlayerSerializer
from .models import Team, Player  # Ensure Player is imported or available via apps.get_model

class TeamSerializer(serializers.ModelSerializer):
    # 1. For Reading: Returns full player objects (Nested)
    players = PlayerSerializer(many=True, read_only=True)

    # 2. For Writing: Accepts a list of IDs (e.g., [1, 2, 5])
    # The 'source' argument maps this back to the 'players' field on your Model
    player_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        write_only=True,
        queryset=Player.objects.all(),
        source='players' 
    )

    class Meta:
        model = Team
        # Add 'player_ids' to the fields list
        fields = ['id', 'name', 'captain', 'players', 'player_ids']