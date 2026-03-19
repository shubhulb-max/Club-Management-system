from django import forms
from django.contrib import admin
from .models import Membership, MembershipLeave, Player, RegistrationRequest, Subscription


class MembershipInline(admin.StackedInline):
    model = Membership
    extra = 0


class SubscriptionInline(admin.StackedInline):
    model = Subscription
    extra = 0


class MembershipLeaveInline(admin.TabularInline):
    model = MembershipLeave
    extra = 0


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
    inlines = (MembershipInline, SubscriptionInline)

    def save_model(self, request, obj, form, change):
        user = obj.user
        if user:
            obj.first_name = user.first_name or ""
            obj.last_name = user.last_name or ""
            obj.phone_number = getattr(user, "phone_number", "") or ""
        super().save_model(request, obj, form, change)

admin.site.register(Player, PlayerAdmin)


@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ("player", "join_date", "status", "fee_exempt")
    list_filter = ("status", "fee_exempt")
    search_fields = ("player__first_name", "player__last_name", "player__phone_number")
    inlines = (MembershipLeaveInline,)


admin.site.register(Subscription)


@admin.register(RegistrationRequest)
class RegistrationRequestAdmin(admin.ModelAdmin):
    list_display = ("phone_number", "first_name", "last_name", "status", "created_at", "approved_at")
    search_fields = ("phone_number", "first_name", "last_name")
    list_filter = ("status",)
    readonly_fields = ("created_at", "updated_at", "approved_at", "approved_by")
