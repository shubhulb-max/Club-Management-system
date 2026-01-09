from rest_framework import serializers
from .models import Player, Membership
from teams.models import Team
from tournaments.models import TournamentParticipation

class MembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Membership
        fields = ['join_date', 'status']

class PlayerTeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id', 'name']

class PlayerTournamentParticipationSerializer(serializers.ModelSerializer):
    tournament_name = serializers.ReadOnlyField(source='tournament.name')
    tournament_start_date = serializers.ReadOnlyField(source='tournament.start_date')

    class Meta:
        model = TournamentParticipation
        fields = ['id', 'tournament', 'tournament_name', 'tournament_start_date']

class PlayerSerializer(serializers.ModelSerializer):
    membership_active = serializers.BooleanField(read_only=True)
    membership = MembershipSerializer(read_only=True)
    teams = PlayerTeamSerializer(many=True, read_only=True)
    captain_of = PlayerTeamSerializer(many=True, read_only=True)
    tournament_participations = PlayerTournamentParticipationSerializer(many=True, read_only=True)

    class Meta:
        model = Player
        fields = [
            'id', 'first_name', 'last_name', 'age', 'role', 'profile_picture',
            'phone_number', 'membership_active', 'membership', 'teams',
            'captain_of', 'tournament_participations'
        ]
