from django.contrib.auth import get_user_model
from django.db import transaction
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
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Player
        fields = [
            'id', 'first_name', 'last_name', 'age', 'role', 'profile_picture',
            'phone_number', 'membership_active', 'membership', 'teams',
            'captain_of', 'tournament_participations', 'password'
        ]

    def validate(self, attrs):
        password = attrs.get('password')
        phone_number = attrs.get('phone_number')
        if password and not phone_number:
            raise serializers.ValidationError({"phone_number": "Phone number is required when setting a password."})
        if password and User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({"phone_number": "Account with this phone number already exists."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        with transaction.atomic():
            player = super().create(validated_data)
            if password:
                user = User.objects.create_user(phone_number=player.phone_number, password=password)
                player.user = user
                player.save(update_fields=['user'])
        return player
User = get_user_model()
