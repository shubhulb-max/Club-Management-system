from rest_framework import serializers

class RegisterSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, required=True)
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    username = serializers.CharField(max_length=150, required=False) # Optional alias for phone_number if needed

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15, required=True)
    password = serializers.CharField(write_only=True, required=True)
