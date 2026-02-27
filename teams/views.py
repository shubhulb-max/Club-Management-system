from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Team
from .serializers import TeamSerializer

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [AllowAny()]
        return [IsAuthenticated()]
