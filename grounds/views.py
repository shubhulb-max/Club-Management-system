from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Ground
from .serializers import GroundSerializer

class GroundViewSet(viewsets.ModelViewSet):
    queryset = Ground.objects.all()
    serializer_class = GroundSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]
