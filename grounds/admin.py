from django.contrib import admin
from .models import Ground

class GroundAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'google_map_link')
    search_fields = ('name', 'location', 'google_map_link')

admin.site.register(Ground, GroundAdmin)
