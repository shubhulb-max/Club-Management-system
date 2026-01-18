from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from matches.models import Match
from players.models import Player
from teams.models import Team
from tournaments.models import Tournament, TournamentParticipation
from grounds.models import Ground
from inventory.models import InventoryItem
from media_gallery.models import Media


class KPIsView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        now = timezone.now()
        today = now.date()
        total_players = Player.objects.count()
        total_matches = Match.objects.count()
        upcoming_matches = Match.objects.filter(date__gte=now).count()
        completed_matches = Match.objects.filter(date__lt=now).count()
        total_teams = Team.objects.count()
        total_grounds = Ground.objects.count()
        total_inventory_items = InventoryItem.objects.count()
        total_media = Media.objects.count()

        total_tournaments = Tournament.objects.count()
        upcoming_tournaments = Tournament.objects.filter(start_date__gte=today).count()
        completed_tournaments = Tournament.objects.filter(start_date__lt=today).count()
        total_tournament_participations = TournamentParticipation.objects.count()

        result_counts = {
            "win": Match.objects.filter(result="win").count(),
            "loss": Match.objects.filter(result="loss").count(),
            "draw": Match.objects.filter(result="draw").count(),
            "no_result": Match.objects.filter(result="no_result").count(),
        }

        return Response({
            "total_players": total_players,
            "total_matches": total_matches,
            "upcoming_matches": upcoming_matches,
            "completed_matches": completed_matches,
            "total_teams": total_teams,
            "total_grounds": total_grounds,
            "total_inventory_items": total_inventory_items,
            "total_media": total_media,
            "total_tournaments": total_tournaments,
            "upcoming_tournaments": upcoming_tournaments,
            "completed_tournaments": completed_tournaments,
            "total_tournament_participations": total_tournament_participations,
            "results": result_counts,
        })
