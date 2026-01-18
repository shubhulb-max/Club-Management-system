from django import forms
from django.contrib import admin
from .models import Player, Membership, Subscription

class PlayerAdminForm(forms.ModelForm):
    class Meta:
        model = Player
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ("first_name", "last_name", "phone_number"):
            if field_name in self.fields:
                self.fields[field_name].required = False

class PlayerAdmin(admin.ModelAdmin):
    form = PlayerAdminForm
    list_display = ('first_name', 'last_name', 'age', 'role', 'phone_number')
    search_fields = ('first_name', 'last_name', 'phone_number')
    list_filter = ('role',)

    def save_model(self, request, obj, form, change):
        user = obj.user
        if user:
            obj.first_name = user.first_name or ""
            obj.last_name = user.last_name or ""
            obj.phone_number = getattr(user, "phone_number", "") or ""
        super().save_model(request, obj, form, change)

admin.site.register(Player, PlayerAdmin)
admin.site.register(Membership)
admin.site.register(Subscription)
