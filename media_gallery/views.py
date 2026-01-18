from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Media
from .serializers import MediaSerializer


class MediaViewSet(viewsets.ModelViewSet):
    queryset = Media.objects.all().order_by("-uploaded_at")
    serializer_class = MediaSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]
