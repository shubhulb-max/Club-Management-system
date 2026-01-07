from rest_framework import serializers
from .models import Tournament, TournamentParticipation
from players.serializers import PlayerSerializer

class TournamentParticipationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TournamentParticipation
        fields = ['id', 'player', 'tournament']

class TournamentSerializer(serializers.ModelSerializer):
    participants = PlayerSerializer(many=True, read_only=True)

    class Meta:
        model = Tournament
        fields = ['id', 'name', 'start_date', 'entry_fee', 'participants']
