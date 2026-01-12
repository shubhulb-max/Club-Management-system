from django.test import TestCase
from .models import Player, Subscription
from financials.models import Transaction
from datetime import date, timedelta
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

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

class ClaimProfileTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = '/api/players/claim-profile/'

        # Create an unclaimed player
        self.unclaimed_player = Player.objects.create(
            first_name="Unclaimed",
            last_name="Player",
            age=20,
            role="bowler",
            phone_number="9876543210"
        )

        # Create a claimed player
        self.claimed_user = User.objects.create_user(username="claimed_user", password="password")
        self.claimed_player = Player.objects.create(
            first_name="Claimed",
            last_name="Player",
            age=22,
            role="batsman",
            phone_number="1122334455",
            user=self.claimed_user
        )

    def test_claim_profile_success(self):
        data = {
            "phone_number": "9876543210",
            "password": "newpassword123"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)

        # Verify linkage
        self.unclaimed_player.refresh_from_db()
        self.assertIsNotNone(self.unclaimed_player.user)
        self.assertEqual(self.unclaimed_player.user.username, "9876543210")

    def test_claim_profile_not_found(self):
        data = {
            "phone_number": "0000000000",
            "password": "password"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_claim_profile_already_claimed(self):
        data = {
            "phone_number": "1122334455",
            "password": "password"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("already linked", response.data["error"])

    def test_claim_profile_missing_data(self):
        data = {"phone_number": "9876543210"} # Missing password
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
