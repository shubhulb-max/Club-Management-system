from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from .models import Media
from .serializers import MediaSerializer


class MediaViewSet(viewsets.ModelViewSet):
    serializer_class = MediaSerializer

    def get_queryset(self):
        queryset = Media.objects.all().order_by("-uploaded_at")
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated and user.is_staff:
            return queryset
        return queryset.filter(is_approved=True)

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        if self.action == "approve":
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(is_approved=False, approved_at=None, approved_by=None)

    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        media = self.get_object()
        if media.is_approved:
            return Response({"detail": "Media is already approved."}, status=status.HTTP_400_BAD_REQUEST)

        media.is_approved = True
        media.approved_at = timezone.now()
        media.approved_by = request.user
        media.save(update_fields=["is_approved", "approved_at", "approved_by"])
        return Response(self.get_serializer(media).data, status=status.HTTP_200_OK)
