from rest_framework import viewsets
from .models import Tournament, TournamentParticipation
from .serializers import TournamentSerializer, TournamentParticipationSerializer

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

class TournamentParticipationViewSet(viewsets.ModelViewSet):
    queryset = TournamentParticipation.objects.all()
    serializer_class = TournamentParticipationSerializer
