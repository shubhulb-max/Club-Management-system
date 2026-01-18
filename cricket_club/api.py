from rest_framework import routers
from media_gallery.views import MediaViewSet
from players.views import PlayerViewSet
from teams.views import TeamViewSet
from matches.views import MatchViewSet
from tournaments.views import TournamentViewSet, TournamentParticipationViewSet
from grounds.views import GroundViewSet
from financials.views import TransactionViewSet
from inventory.views import (
    InventoryCategoryViewSet,
    InventoryItemViewSet,
    ItemAssignmentViewSet,
    SaleViewSet,
)

router = routers.DefaultRouter()
router.register(r'players', PlayerViewSet)
router.register(r'teams', TeamViewSet)
router.register(r'matches', MatchViewSet)
router.register(r'tournaments', TournamentViewSet)
router.register(r'tournament-participations', TournamentParticipationViewSet)
router.register(r'grounds', GroundViewSet)
router.register(r'media', MediaViewSet)
router.register(r'transactions', TransactionViewSet)
router.register(r'inventory-categories', InventoryCategoryViewSet)
router.register(r'inventory-items', InventoryItemViewSet)
router.register(r'item-assignments', ItemAssignmentViewSet)
router.register(r'sales', SaleViewSet)
