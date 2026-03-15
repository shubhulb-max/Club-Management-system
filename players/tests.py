from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import Player, RegistrationRequest, Subscription
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
        self.registration_list_url = '/api/auth/registrations/'

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
        self.assertEqual(response.data["status"], "pending_approval")

        User = get_user_model()
        self.assertFalse(User.objects.filter(phone_number="1234567890").exists())
        registration = RegistrationRequest.objects.get(phone_number="1234567890")
        self.assertEqual(registration.first_name, "New")
        self.assertEqual(registration.status, RegistrationRequest.STATUS_PENDING)

    def test_register_existing_player_creates_pending_request(self):
        data = {
            "phone_number": "9988776655",
            "password": "password123",
            "first_name": "Updated",
            "last_name": "Name"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        registration = RegistrationRequest.objects.get(phone_number="9988776655")
        self.assertEqual(registration.first_name, "Updated")
        self.assertEqual(registration.last_name, "Name")
        self.unclaimed_player.refresh_from_db()
        self.assertIsNone(self.unclaimed_player.user)
        self.assertEqual(self.unclaimed_player.first_name, "Existing")
        self.assertEqual(self.unclaimed_player.last_name, "Player")

    def test_register_existing_user_fail(self):
        User = get_user_model()
        User.objects.create_user(phone_number="1234567890", password="password")

        data = {
            "phone_number": "1234567890",
            "password": "password123",
            "first_name": "Existing",
            "last_name": "User"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_rejects_pending_registration(self):
        self.client.post(
            self.register_url,
            {
                "phone_number": "1234567890",
                "password": "password123",
                "first_name": "Pending",
                "last_name": "User",
            },
        )

        response = self.client.post(
            self.login_url,
            {
                "phone_number": "1234567890",
                "password": "password123",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("pending", str(response.data).lower())

    def test_admin_can_list_and_approve_registration(self):
        register_response = self.client.post(
            self.register_url,
            {
                "phone_number": "9988776655",
                "password": "password123",
                "first_name": "Updated",
                "last_name": "Name",
            },
        )
        registration_id = register_response.data["registration_id"]

        User = get_user_model()
        admin_user = User.objects.create_user(phone_number="7777777777", password="password", is_staff=True)
        self.client.force_authenticate(user=admin_user)

        list_response = self.client.get(self.registration_list_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(list_response.data[0]["phone_number"], "9988776655")

        approve_response = self.client.post(
            f"/api/auth/registrations/{registration_id}/approve/",
            {"role": "bowler", "age": 26},
            format="json",
        )
        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)

        self.unclaimed_player.refresh_from_db()
        self.assertIsNotNone(self.unclaimed_player.user)
        self.assertEqual(self.unclaimed_player.user.phone_number, "9988776655")
        self.assertEqual(self.unclaimed_player.first_name, "Updated")
        self.assertEqual(self.unclaimed_player.last_name, "Name")

        registration = RegistrationRequest.objects.get(id=registration_id)
        self.assertEqual(registration.status, RegistrationRequest.STATUS_APPROVED)
        self.assertEqual(registration.approved_by, admin_user)

        self.client.force_authenticate(user=None)
        login_response = self.client.post(
            self.login_url,
            {"phone_number": "9988776655", "password": "password123"},
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)

    def test_login_success(self):
        User = get_user_model()
        User.objects.create_user(phone_number="9999999999", password="password123")

        data = {
            "phone_number": "9999999999",
            "password": "password123"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_login_fail(self):
        data = {
            "phone_number": "9999999999",
            "password": "wrongpassword"
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
