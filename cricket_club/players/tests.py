from django.test import TestCase
from .models import Player, Membership
from financials.models import Transaction
import datetime

class PlayerSignalTest(TestCase):

    def test_membership_and_fee_creation_on_player_creation(self):
        # Create a new player
        player = Player.objects.create(
            first_name="Signal",
            last_name="Test",
            age=28,
            role="all_rounder"
        )

        # Check if a membership was created
        self.assertTrue(Membership.objects.filter(player=player).exists())
        membership = Membership.objects.get(player=player)
        self.assertEqual(membership.status, 'pending')

        # Check if a one-time fee transaction was created
        self.assertTrue(Transaction.objects.filter(player=player).exists())
        transaction = Transaction.objects.get(player=player)
        self.assertEqual(transaction.amount, 2000.00)
        self.assertEqual(transaction.description, f"One-time membership fee for {player}")

class MembershipModelTest(TestCase):

    def setUp(self):
        # Creating a player will trigger the signal
        self.player = Player.objects.create(first_name="Jane", last_name="Smith", age=22, role="bowler")

    def test_membership_creation(self):
        # The membership is now created by the signal, so we just retrieve it
        membership = Membership.objects.get(player=self.player)
        self.assertEqual(membership.status, "pending") # Should be pending initially
        self.assertEqual(membership.join_date, datetime.date.today())
        self.assertEqual(str(membership), "Jane Smith's Membership")

        # We can still test updating the membership
        membership.status = "active"
        membership.save()
        updated_membership = Membership.objects.get(player=self.player)
        self.assertEqual(updated_membership.status, "active")
