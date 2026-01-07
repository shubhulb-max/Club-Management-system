from django.test import TestCase
from django.core.management import call_command
from players.models import Player
from financials.models import Transaction
from datetime import date, timedelta

class GenerateMonthlyFeesTest(TestCase):

    def setUp(self):
        self.active_player = Player.objects.create(first_name='Active', last_name='Player', age=25, role='batsman')
        self.overdue_player = Player.objects.create(first_name='Overdue', last_name='Player', age=30, role='all_rounder')

        # Make the overdue player's membership inactive
        Transaction.objects.create(
            player=self.overdue_player,
            category='monthly',
            amount=750,
            due_date=date.today() - timedelta(days=31),
            paid=False
        )

    def test_generate_monthly_fees_command(self):
        # Run the management command
        call_command('generate_monthly_fees')

        # Check that a new transaction was created for the active player
        self.assertTrue(
            Transaction.objects.filter(
                player=self.active_player,
                category='monthly',
                paid=False
            ).exists()
        )

        # Check that no new transaction was created for the overdue player
        self.assertEqual(
            Transaction.objects.filter(player=self.overdue_player, category='monthly').count(),
            1 # Only the initial overdue one should exist
        )

        # Run the command again to test idempotency
        call_command('generate_monthly_fees')
        self.assertEqual(
            Transaction.objects.filter(player=self.active_player, category='monthly').count(),
            1 # Should not create a duplicate
        )
