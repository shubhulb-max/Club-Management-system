from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
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

class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'

        # Create an unclaimed player
        self.unclaimed_player = Player.objects.create(
            first_name="Existing",
            last_name="Player",
            age=25,
            role="bowler",
            phone_number="9988776655"
        )

    def test_register_new_player(self):
        data = {
            "phone_number": "1234567890",
            "password": "password123",
            "first_name": "New",
            "last_name": "User"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("token", response.data)

        # Verify user and player created
        user = User.objects.get(username="1234567890")
        player = Player.objects.get(phone_number="1234567890")
        self.assertEqual(player.user, user)
        self.assertEqual(player.first_name, "New")

    def test_register_claim_existing_player(self):
        data = {
            "phone_number": "9988776655",
            "password": "password123"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verify linkage
        self.unclaimed_player.refresh_from_db()
        self.assertIsNotNone(self.unclaimed_player.user)
        self.assertEqual(self.unclaimed_player.user.username, "9988776655")

    def test_register_existing_user_fail(self):
        # First register
        User.objects.create_user(username="1234567890", password="password")

        # Try registering again
        data = {
            "phone_number": "1234567890",
            "password": "password123"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        User.objects.create_user(username="9999999999", password="password123")

        data = {
            "phone_number": "9999999999",
            "password": "password123"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)

    def test_login_fail(self):
        data = {
            "phone_number": "9999999999",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
