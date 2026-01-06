from django.contrib import admin
from .models import InventoryItem, ItemAssignment, Sale

class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'quantity', 'price')
    list_filter = ('type',)
    search_fields = ('name', 'description')

class ItemAssignmentAdmin(admin.ModelAdmin):
    list_display = ('item', 'team', 'quantity_assigned', 'date_assigned')
    search_fields = ('item__name', 'team__name')
    list_filter = ('date_assigned',)

class SaleAdmin(admin.ModelAdmin):
    list_display = ('item', 'player', 'quantity_sold', 'sale_date')
    search_fields = ('item__name', 'player__first_name', 'player__last_name')
    list_filter = ('sale_date',)

admin.site.register(InventoryItem, InventoryItemAdmin)
admin.site.register(ItemAssignment, ItemAssignmentAdmin)
admin.site.register(Sale, SaleAdmin)
