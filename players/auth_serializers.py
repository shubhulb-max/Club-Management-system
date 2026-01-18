from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from rest_framework import serializers

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
