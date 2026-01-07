from django.contrib import admin
from .models import Ground

class GroundAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')

admin.site.register(Ground, GroundAdmin)
