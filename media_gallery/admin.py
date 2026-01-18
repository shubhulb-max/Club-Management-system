from django.contrib import admin
from .models import Media


@admin.register(Media)
class MediaAdmin(admin.ModelAdmin):
    list_display = ("title", "media_type", "uploaded_at")
    search_fields = ("title", "file")
    list_filter = ("media_type", "uploaded_at")
