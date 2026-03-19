from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import serializers
from accounts.phone_utils import normalize_phone_number
from cricket_club.upload_validators import validate_uploaded_image
from .models import Player, Membership, MembershipLeave
from teams.models import Team
from tournaments.models import TournamentParticipation

class MembershipLeaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipLeave
        fields = ["id", "start_date", "end_date", "reason"]


class MembershipSerializer(serializers.ModelSerializer):
    leave_periods = MembershipLeaveSerializer(many=True, read_only=True)

    class Meta:
        model = Membership
        fields = ['join_date', 'status', 'fee_exempt', 'fee_exempt_reason', 'leave_periods']

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
    membership_join_date = serializers.DateField(write_only=True, required=False)
    membership_status = serializers.ChoiceField(
        choices=Membership.STATUS_CHOICES,
        write_only=True,
        required=False,
    )
    membership_fee_exempt = serializers.BooleanField(write_only=True, required=False)
    membership_fee_exempt_reason = serializers.CharField(write_only=True, required=False, allow_blank=True)
    teams = PlayerTeamSerializer(many=True, read_only=True)
    captain_of = PlayerTeamSerializer(many=True, read_only=True)
    tournament_participations = PlayerTournamentParticipationSerializer(many=True, read_only=True)
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Player
        fields = [
            'id', 'first_name', 'last_name', 'age', 'role', 'profile_picture',
            'phone_number', 'membership_active', 'membership', 'teams',
            'captain_of', 'tournament_participations', 'password',
            'membership_join_date', 'membership_status',
            'membership_fee_exempt', 'membership_fee_exempt_reason',
        ]

    def validate_phone_number(self, value):
        if value in (None, ""):
            return value
        try:
            return normalize_phone_number(value)
        except ValidationError as exc:
            raise serializers.ValidationError(str(exc))

    def validate(self, attrs):
        password = attrs.get('password')
        phone_number = attrs.get('phone_number')
        if password and not phone_number:
            raise serializers.ValidationError({"phone_number": "Phone number is required when setting a password."})
        if password and User.objects.filter(phone_number=phone_number).exists():
            raise serializers.ValidationError({"phone_number": "Account with this phone number already exists."})
        return attrs

    def validate_profile_picture(self, value):
        return validate_uploaded_image(value)

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        membership_join_date = validated_data.pop('membership_join_date', None)
        membership_status = validated_data.pop('membership_status', None)
        membership_fee_exempt = validated_data.pop('membership_fee_exempt', None)
        membership_fee_exempt_reason = validated_data.pop('membership_fee_exempt_reason', None)
        with transaction.atomic():
            player = super().create(validated_data)
            membership = getattr(player, "membership", None)
            membership_updates = []
            if membership and membership_join_date is not None:
                membership.join_date = membership_join_date
                membership_updates.append("join_date")
            if membership and membership_status is not None:
                membership.status = membership_status
                membership_updates.append("status")
            if membership and membership_fee_exempt is not None:
                membership.fee_exempt = membership_fee_exempt
                membership_updates.append("fee_exempt")
            if membership and membership_fee_exempt_reason is not None:
                membership.fee_exempt_reason = membership_fee_exempt_reason
                membership_updates.append("fee_exempt_reason")
            if membership_updates:
                membership.save(update_fields=membership_updates)
            if password:
                user = User.objects.create_user(phone_number=player.phone_number, password=password)
                player.user = user
                player.save(update_fields=['user'])
        return player

    def update(self, instance, validated_data):
        membership_join_date = validated_data.pop('membership_join_date', None)
        membership_status = validated_data.pop('membership_status', None)
        membership_fee_exempt = validated_data.pop('membership_fee_exempt', None)
        membership_fee_exempt_reason = validated_data.pop('membership_fee_exempt_reason', None)
        player = super().update(instance, validated_data)
        membership = getattr(player, "membership", None)
        membership_updates = []
        if membership and membership_join_date is not None:
            membership.join_date = membership_join_date
            membership_updates.append("join_date")
        if membership and membership_status is not None:
            membership.status = membership_status
            membership_updates.append("status")
        if membership and membership_fee_exempt is not None:
            membership.fee_exempt = membership_fee_exempt
            membership_updates.append("fee_exempt")
        if membership and membership_fee_exempt_reason is not None:
            membership.fee_exempt_reason = membership_fee_exempt_reason
            membership_updates.append("fee_exempt_reason")
        if membership_updates:
            membership.save(update_fields=membership_updates)
        return player
User = get_user_model()
