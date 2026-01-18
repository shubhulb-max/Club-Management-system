from django.db import models

class Ground(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    google_map_link = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return self.name
