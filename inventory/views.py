from rest_framework import viewsets
from .models import InventoryCategory, InventoryItem, ItemAssignment, Sale
from .serializers import (
    InventoryCategorySerializer,
    InventoryItemSerializer,
    ItemAssignmentSerializer,
    SaleSerializer,
)


class InventoryCategoryViewSet(viewsets.ModelViewSet):
    queryset = InventoryCategory.objects.all()
    serializer_class = InventoryCategorySerializer

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer

class ItemAssignmentViewSet(viewsets.ModelViewSet):
    queryset = ItemAssignment.objects.all()
    serializer_class = ItemAssignmentSerializer

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
