from rest_framework import serializers
from .models import InventoryCategory, InventoryItem, ItemAssignment, Sale


class InventoryCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryCategory
        fields = ['id', 'name', 'description', 'image']

class InventoryItemSerializer(serializers.ModelSerializer):
    category_detail = InventoryCategorySerializer(source='category', read_only=True)

    class Meta:
        model = InventoryItem
        fields = [
            'id',
            'category',
            'category_detail',
            'name',
            'description',
            'quantity',
            'available_quantity',
            'missing_quantity',
            'destroyed_quantity',
            'distributed_quantity',
            'price',
            'type',
        ]

class ItemAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemAssignment
        fields = ['id', 'item', 'team', 'quantity_assigned', 'date_assigned']

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = ['id', 'item', 'player', 'quantity_sold', 'sale_date']
