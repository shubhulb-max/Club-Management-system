from rest_framework import serializers
from cricket_club.upload_validators import validate_uploaded_image
from .models import Media


class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = [
            "id",
            "title",
            "file",
            "media_type",
            "is_approved",
            "approved_at",
            "approved_by",
            "uploaded_at",
        ]
        read_only_fields = ["is_approved", "approved_at", "approved_by", "uploaded_at"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        media_type = attrs.get("media_type") or getattr(self.instance, "media_type", None)
        file_obj = attrs.get("file")
        if media_type == "photo" and file_obj:
            validate_uploaded_image(file_obj)
        return attrs
