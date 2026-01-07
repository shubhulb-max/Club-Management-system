from rest_framework import serializers
from .models import InventoryItem, ItemAssignment, Sale

class InventoryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItem
        fields = ['id', 'name', 'description', 'quantity', 'price', 'type']

class ItemAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemAssignment
        fields = ['id', 'item', 'team', 'quantity_assigned', 'date_assigned']

class SaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sale
        fields = ['id', 'item', 'player', 'quantity_sold', 'sale_date']
