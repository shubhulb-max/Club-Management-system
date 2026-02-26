from rest_framework import viewsets
from .models import Match, Lineup
from .serializers import MatchSerializer, LineupSerializer

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer


class LineupViewSet(viewsets.ModelViewSet):
    queryset = Lineup.objects.all()
    serializer_class = LineupSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        match_id = self.request.query_params.get("match")
        team_id = self.request.query_params.get("team")
        if match_id:
            queryset = queryset.filter(match_id=match_id)
        if team_id:
            queryset = queryset.filter(team_id=team_id)
        return queryset
