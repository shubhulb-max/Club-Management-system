from django.contrib import admin
from .models import InventoryCategory, InventoryItem, ItemAssignment, Sale

class InventoryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class InventoryItemAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'category',
        'type',
        'quantity',
        'available_quantity',
        'missing_quantity',
        'destroyed_quantity',
        'distributed_quantity',
        'price',
    )
    list_filter = ('type', 'category')
    search_fields = ('name', 'description')

class ItemAssignmentAdmin(admin.ModelAdmin):
    list_display = ('item', 'team', 'quantity_assigned', 'date_assigned')
    search_fields = ('item__name', 'team__name')
    list_filter = ('date_assigned',)

class SaleAdmin(admin.ModelAdmin):
    list_display = ('item', 'player', 'quantity_sold', 'sale_date')
    search_fields = ('item__name', 'player__first_name', 'player__last_name')
    list_filter = ('sale_date',)

admin.site.register(InventoryCategory, InventoryCategoryAdmin)
admin.site.register(InventoryItem, InventoryItemAdmin)
admin.site.register(ItemAssignment, ItemAssignmentAdmin)
admin.site.register(Sale, SaleAdmin)
