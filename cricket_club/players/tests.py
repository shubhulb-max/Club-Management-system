from django.test import TestCase
from .models import Player, Subscription
from financials.models import Transaction
from datetime import date, timedelta

class PlayerModelTest(TestCase):

    def setUp(self):
        self.player = Player.objects.create(
            first_name="John",
            last_name="Doe",
            age=25,
            role="batsman"
        )

    def test_subscription_creation_on_player_creation(self):
        self.assertTrue(Subscription.objects.filter(player=self.player).exists())

    def test_membership_active_property(self):
        # Initially, the player should be active as there are no overdue invoices
        self.assertTrue(self.player.membership_active)

        # Create an unpaid, overdue monthly fee
        Transaction.objects.create(
            player=self.player,
            category='monthly',
            amount=750,
            due_date=date.today() - timedelta(days=31),
            paid=False
        )
        self.assertFalse(self.player.membership_active)

        # Mark the fee as paid
        Transaction.objects.filter(player=self.player, category='monthly').update(paid=True)
        self.assertTrue(self.player.membership_active)
