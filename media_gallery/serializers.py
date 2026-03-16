from rest_framework import serializers
from cricket_club.upload_validators import validate_uploaded_image
from .models import Media


class MediaSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.SerializerMethodField()
    approved_by_name = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = [
            "id",
            "title",
            "file",
            "media_type",
            "uploaded_by",
            "uploaded_by_name",
            "is_approved",
            "approved_at",
            "approved_by",
            "approved_by_name",
            "uploaded_at",
        ]
        read_only_fields = [
            "uploaded_by",
            "uploaded_by_name",
            "is_approved",
            "approved_at",
            "approved_by",
            "approved_by_name",
            "uploaded_at",
        ]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        media_type = attrs.get("media_type") or getattr(self.instance, "media_type", None)
        file_obj = attrs.get("file")
        if media_type == "photo" and file_obj:
            validate_uploaded_image(file_obj)
        return attrs

    def get_uploaded_by_name(self, obj):
        return self._get_user_display_name(obj.uploaded_by)

    def get_approved_by_name(self, obj):
        return self._get_user_display_name(obj.approved_by)

    def _get_user_display_name(self, user):
        if not user:
            return None
        full_name = f"{user.first_name} {user.last_name}".strip()
        return full_name or user.phone_number
