from django.contrib import admin
from .models import Team

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'captain')
    search_fields = ('name',)

admin.site.register(Team, TeamAdmin)
