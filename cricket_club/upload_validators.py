import os

from PIL import Image, UnidentifiedImageError
from rest_framework import serializers


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP", "GIF"}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024


def validate_uploaded_image(file_obj):
    if not file_obj:
        return file_obj

    extension = os.path.splitext(file_obj.name or "")[1].lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise serializers.ValidationError(
            "Unsupported image file type. Allowed: jpg, jpeg, png, webp, gif."
        )

    if getattr(file_obj, "size", 0) > MAX_IMAGE_SIZE_BYTES:
        raise serializers.ValidationError("Image size must be 5 MB or smaller.")

    content_type = getattr(file_obj, "content_type", "")
    if content_type and not content_type.startswith("image/"):
        raise serializers.ValidationError("Uploaded file is not an image.")

    try:
        file_obj.seek(0)
        with Image.open(file_obj) as image:
            image.verify()
            if image.format not in ALLOWED_IMAGE_FORMATS:
                raise serializers.ValidationError(
                    "Unsupported image format. Allowed: JPEG, PNG, WEBP, GIF."
                )
    except (UnidentifiedImageError, OSError, ValueError):
        raise serializers.ValidationError("Uploaded file is not a valid image.")
    finally:
        file_obj.seek(0)

    return file_obj
