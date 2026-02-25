from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

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
        data.update({
            "role": "player",
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "player_id": player.id if player else None,
            "player_role": player.role if player else None,
            "dashboard_url": "/api/auth/dashboard/",
        })
        return data
