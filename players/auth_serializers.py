from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from django.db import transaction
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Player

class RegisterSerializer(serializers.Serializer):
    phone_validator = RegexValidator(
        regex=r"^\d{10,15}$",
        message="Phone number must be 10 to 15 digits."
    )
    phone_number = serializers.CharField(max_length=15, required=True, validators=[phone_validator])
    password = serializers.CharField(write_only=True, required=True, trim_whitespace=False)
    first_name = serializers.CharField(max_length=50, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=50, required=False, allow_blank=True)

    def validate_password(self, value):
        validate_password(value)
        return value

class LoginSerializer(serializers.Serializer):
    phone_validator = RegexValidator(
        regex=r"^\d{10,15}$",
        message="Phone number must be 10 to 15 digits."
    )
    phone_number = serializers.CharField(max_length=15, required=True, validators=[phone_validator])
    password = serializers.CharField(write_only=True, required=True, trim_whitespace=False)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def _sync_user_names_from_player(self, user, player):
        updated_fields = []
        if player.first_name and not user.first_name:
            user.first_name = player.first_name
            updated_fields.append("first_name")
        if player.last_name and not user.last_name:
            user.last_name = player.last_name
            updated_fields.append("last_name")
        if updated_fields:
            user.save(update_fields=updated_fields)

    def _claim_player_for_user(self, user):
        phone_number = getattr(user, "phone_number", None)
        if not phone_number:
            return None
        with transaction.atomic():
            player = Player.objects.select_for_update().filter(phone_number=phone_number).first()
            if not player:
                return None
            if player.user_id and player.user_id != user.id:
                return player
            if not player.user_id:
                player.user = user
                player.save(update_fields=["user"])
            self._sync_user_names_from_player(user, player)
        return player

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        player = getattr(user, "player", None)
        token["role"] = "player"
        token["first_name"] = user.first_name or ""
        token["last_name"] = user.last_name or ""
        token["player_id"] = player.id if player else None
        token["player_role"] = player.role if player else None
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        player = getattr(user, "player", None)
        if player:
            self._sync_user_names_from_player(user, player)
        else:
            player = self._claim_player_for_user(user)
            if player:
                user.refresh_from_db(fields=["first_name", "last_name"])

        refresh = self.get_token(user)
        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)

        if not player:
            player = getattr(user, "player", None)
        data.update({
            "role": "player",
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "player_id": player.id if player else None,
            "player_role": player.role if player else None,
            "dashboard_url": "/api/auth/dashboard/",
        })
        return data
