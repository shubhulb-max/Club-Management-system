from rest_framework import viewsets
from .models import InventoryItem, ItemAssignment, Sale
from .serializers import InventoryItemSerializer, ItemAssignmentSerializer, SaleSerializer

class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemSerializer

class ItemAssignmentViewSet(viewsets.ModelViewSet):
    queryset = ItemAssignment.objects.all()
    serializer_class = ItemAssignmentSerializer

class SaleViewSet(viewsets.ModelViewSet):
    queryset = Sale.objects.all()
    serializer_class = SaleSerializer
