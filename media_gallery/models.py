from django.db import models


class Media(models.Model):
    MEDIA_TYPE_CHOICES = [
        ("photo", "Photo"),
        ("video", "Video"),
        ("other", "Other"),
    ]

    title = models.CharField(max_length=100, blank=True)
    file = models.FileField(upload_to="media_uploads/")
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or self.file.name
