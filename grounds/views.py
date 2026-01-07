from rest_framework import viewsets
from .models import Ground
from .serializers import GroundSerializer

class GroundViewSet(viewsets.ModelViewSet):
    queryset = Ground.objects.all()
    serializer_class = GroundSerializer
