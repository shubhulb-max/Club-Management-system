from rest_framework import serializers
from .models import Player

class PlayerSerializer(serializers.ModelSerializer):
    membership_active = serializers.BooleanField(read_only=True)

    class Meta:
        model = Player
        fields = ['id', 'first_name', 'last_name', 'age', 'role', 'profile_picture', 'phone_number', 'membership_active']
