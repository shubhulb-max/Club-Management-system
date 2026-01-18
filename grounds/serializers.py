from rest_framework import serializers
from .models import Ground

class GroundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ground
        fields = ['id', 'name', 'location', 'google_map_link']
