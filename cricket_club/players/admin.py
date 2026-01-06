from django.contrib import admin
from .models import Player, Membership

class PlayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'age', 'role', 'phone_number')
    search_fields = ('first_name', 'last_name', 'phone_number')
    list_filter = ('role',)

admin.site.register(Player, PlayerAdmin)
admin.site.register(Membership)
