from django.test import TestCase
from .models import Tournament, TournamentParticipation
from players.models import Player
from financials.models import Transaction
from datetime import date

class TournamentSignalTest(TestCase):

    def setUp(self):
        self.player = Player.objects.create(first_name='Tournament', last_name='Test', age=29, role='wicket_keeper')
        self.tournament = Tournament.objects.create(
            name='Club Championship',
            start_date=date.today(),
            entry_fee=500.00
        )

    def test_fee_creation_on_participation(self):
        # Create a new tournament participation
        TournamentParticipation.objects.create(
            player=self.player,
            tournament=self.tournament
        )

        # Check if a tournament fee transaction was created
        self.assertTrue(
            Transaction.objects.filter(
                player=self.player,
                category='tournament',
                amount=500.00,
                paid=False
            ).exists()
        )
