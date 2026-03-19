from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from PIL import Image
from io import BytesIO
from .models import LeaveRequest, MembershipLeave, Player, RegistrationRequest, Subscription
from financials.models import Transaction
from datetime import date, timedelta

VALID_PASSWORD = "Str0ngPass!234"


class PlayerModelTest(TestCase):

    def setUp(self):
        self.player = Player.objects.create(
            first_name="John",
            last_name="Doe",
            age=25,
            role="top_order_batter"
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

    def test_membership_becomes_inactive_after_thirty_days_overdue(self):
        self.player.membership.status = "active"
        self.player.membership.save(update_fields=["status"])
        Transaction.objects.create(
            player=self.player,
            category='monthly',
            amount=750,
            due_date=date.today() - timedelta(days=31),
            paid=False
        )

        status_value = self.player.sync_membership_status()

        self.assertEqual(status_value, "inactive")
        self.player.membership.refresh_from_db()
        self.assertEqual(self.player.membership.status, "inactive")

    def test_membership_becomes_left_after_ninety_days_overdue(self):
        self.player.membership.status = "active"
        self.player.membership.save(update_fields=["status"])
        Transaction.objects.create(
            player=self.player,
            category='monthly',
            amount=750,
            due_date=date.today() - timedelta(days=91),
            paid=False
        )

        status_value = self.player.sync_membership_status()

        self.assertEqual(status_value, "left")
        self.player.membership.refresh_from_db()
        self.assertEqual(self.player.membership.status, "left")

    def test_waived_monthly_invoice_does_not_lapse_membership(self):
        self.player.membership.status = "active"
        self.player.membership.save(update_fields=["status"])
        Transaction.objects.create(
            player=self.player,
            category='monthly',
            amount=750,
            due_date=date.today() - timedelta(days=91),
            paid=False,
            waived=True,
            waived_reason="Approved waiver",
        )

        status_value = self.player.sync_membership_status()

        self.assertEqual(status_value, "active")
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
            "password": VALID_PASSWORD,
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
            "password": VALID_PASSWORD,
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
        User.objects.create_user(phone_number="1234567890", password=VALID_PASSWORD)

        data = {
            "phone_number": "1234567890",
            "password": VALID_PASSWORD,
            "first_name": "Existing",
            "last_name": "User"
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_register_normalizes_indian_prefixes_for_duplicate_check(self):
        User = get_user_model()
        User.objects.create_user(phone_number="9876543210", password=VALID_PASSWORD)

        response = self.client.post(
            self.register_url,
            {
                "phone_number": "+91 98765 43210",
                "password": VALID_PASSWORD,
                "first_name": "Existing",
                "last_name": "User",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_accepts_phone_number_with_country_code(self):
        User = get_user_model()
        User.objects.create_user(phone_number="9999999999", password=VALID_PASSWORD)

        response = self.client.post(
            self.login_url,
            {
                "phone_number": "+91 99999 99999",
                "password": VALID_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_register_stores_normalized_phone_number(self):
        response = self.client.post(
            self.register_url,
            {
                "phone_number": "09876543210",
                "password": VALID_PASSWORD,
                "first_name": "Zero",
                "last_name": "Prefix",
            },
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        registration = RegistrationRequest.objects.get(id=response.data["registration_id"])
        self.assertEqual(registration.phone_number, "9876543210")

    def test_login_rejects_pending_registration(self):
        self.client.post(
            self.register_url,
            {
                "phone_number": "1234567890",
                "password": VALID_PASSWORD,
                "first_name": "Pending",
                "last_name": "User",
            },
        )

        response = self.client.post(
            self.login_url,
            {
                "phone_number": "1234567890",
                "password": VALID_PASSWORD,
            },
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("pending", str(response.data).lower())

    def test_admin_can_list_and_approve_registration(self):
        register_response = self.client.post(
            self.register_url,
            {
                "phone_number": "9988776655",
                "password": VALID_PASSWORD,
                "first_name": "Updated",
                "last_name": "Name",
            },
        )
        registration_id = register_response.data["registration_id"]

        User = get_user_model()
        admin_user = User.objects.create_user(phone_number="7777777777", password=VALID_PASSWORD, is_staff=True)
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
            {"phone_number": "9988776655", "password": VALID_PASSWORD},
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", login_response.data)

    def test_admin_can_reject_registration(self):
        register_response = self.client.post(
            self.register_url,
            {
                "phone_number": "9123456789",
                "password": VALID_PASSWORD,
                "first_name": "Declined",
                "last_name": "User",
            },
        )
        registration_id = register_response.data["registration_id"]

        User = get_user_model()
        admin_user = User.objects.create_user(phone_number="7666666666", password=VALID_PASSWORD, is_staff=True)
        self.client.force_authenticate(user=admin_user)

        reject_response = self.client.post(
            f"/api/auth/registrations/{registration_id}/reject/",
            format="json",
        )
        self.assertEqual(reject_response.status_code, status.HTTP_200_OK)
        self.assertEqual(reject_response.data["status"], RegistrationRequest.STATUS_REJECTED)

        registration = RegistrationRequest.objects.get(id=registration_id)
        self.assertEqual(registration.status, RegistrationRequest.STATUS_REJECTED)
        self.assertEqual(registration.approved_by, admin_user)

        User = get_user_model()
        self.assertFalse(User.objects.filter(phone_number="9123456789").exists())

        self.client.force_authenticate(user=None)
        login_response = self.client.post(
            self.login_url,
            {"phone_number": "9123456789", "password": VALID_PASSWORD},
        )
        self.assertEqual(login_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("rejected", str(login_response.data).lower())

    def test_login_success(self):
        User = get_user_model()
        User.objects.create_user(phone_number="9999999999", password=VALID_PASSWORD)

        data = {
            "phone_number": "9999999999",
            "password": VALID_PASSWORD
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


class PlayerImageUploadValidationTests(TestCase):
    def _build_test_image(self, name="profile.png", image_format="PNG"):
        buffer = BytesIO()
        image = Image.new("RGB", (20, 20), color="red")
        image.save(buffer, format=image_format)
        buffer.seek(0)
        return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")

    def test_rejects_fake_profile_picture(self):
        client = APIClient()
        user = get_user_model().objects.create_user(phone_number="8888888888", password=VALID_PASSWORD)
        client.force_authenticate(user=user)

        response = client.post(
            "/api/players/",
            {
                "first_name": "Fake",
                "last_name": "Image",
                "age": 23,
                "role": "bowler",
                "phone_number": "1111111111",
                "profile_picture": SimpleUploadedFile(
                    "fake.png",
                    b"not an actual image",
                    content_type="image/png",
                ),
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("profile_picture", response.data)

    def test_accepts_valid_profile_picture(self):
        client = APIClient()
        user = get_user_model().objects.create_user(phone_number="8877777777", password=VALID_PASSWORD)
        client.force_authenticate(user=user)

        response = client.post(
            "/api/players/",
            {
                "first_name": "Valid",
                "last_name": "Image",
                "age": 24,
                "role": "top_order_batter",
                "phone_number": "2222222222",
                "profile_picture": self._build_test_image(),
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class PlayerMembershipManualFieldsTests(TestCase):
    def test_can_set_membership_join_date_and_status_on_create(self):
        client = APIClient()
        user = get_user_model().objects.create_user(phone_number="8866666666", password=VALID_PASSWORD)
        client.force_authenticate(user=user)

        response = client.post(
            "/api/players/",
            {
                "first_name": "Legacy",
                "last_name": "Member",
                "age": 30,
                "role": "all_rounder",
                "phone_number": "3333333333",
                "membership_join_date": "2024-11-01",
                "membership_status": "active",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        player = Player.objects.get(phone_number="3333333333")
        self.assertEqual(player.membership.join_date.isoformat(), "2024-11-01")
        self.assertEqual(player.membership.status, "active")

    def test_can_set_membership_fee_exemption_on_create(self):
        client = APIClient()
        user = get_user_model().objects.create_user(phone_number="8855555555", password=VALID_PASSWORD)
        client.force_authenticate(user=user)

        response = client.post(
            "/api/players/",
            {
                "first_name": "Exempt",
                "last_name": "Member",
                "age": 31,
                "role": "bowler",
                "phone_number": "4444444444",
                "membership_join_date": "2024-11-01",
                "membership_status": "active",
                "membership_fee_exempt": True,
                "membership_fee_exempt_reason": "Club management exemption",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        player = Player.objects.get(phone_number="4444444444")
        self.assertTrue(player.membership.fee_exempt)
        self.assertEqual(player.membership.fee_exempt_reason, "Club management exemption")


class MembershipLeaveApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            phone_number="8844444444",
            password=VALID_PASSWORD,
            is_staff=True,
        )
        self.player = Player.objects.create(
            first_name="Leave",
            last_name="Member",
            age=28,
            role="bowler",
            phone_number="5555555555",
        )
        self.client.force_authenticate(user=self.admin_user)
        self.list_url = f"/api/auth/players/{self.player.id}/membership-leaves/"

    def test_admin_can_create_and_list_membership_leave(self):
        create_response = self.client.post(
            self.list_url,
            {
                "start_date": "2025-02-01",
                "end_date": "2025-02-28",
                "reason": "Approved leave",
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data["reason"], "Approved leave")

        list_response = self.client.get(self.list_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(list_response.data[0]["start_date"], "2025-02-01")

    def test_admin_can_update_and_delete_membership_leave(self):
        leave_period = MembershipLeave.objects.create(
            membership=self.player.membership,
            start_date=date(2025, 2, 1),
            end_date=date(2025, 2, 28),
            reason="Initial reason",
        )
        detail_url = f"/api/auth/membership-leaves/{leave_period.id}/"

        update_response = self.client.patch(
            detail_url,
            {"reason": "Updated leave reason", "end_date": "2025-03-05"},
            format="json",
        )

        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["reason"], "Updated leave reason")
        self.assertEqual(update_response.data["end_date"], "2025-03-05")

        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(MembershipLeave.objects.filter(id=leave_period.id).exists())


class LeaveRequestApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.player_user = User.objects.create_user(phone_number="8833333333", password=VALID_PASSWORD)
        self.player = Player.objects.create(
            user=self.player_user,
            first_name="Request",
            last_name="Player",
            age=27,
            role="all_rounder",
            phone_number="6666666666",
        )
        self.admin_user = User.objects.create_user(
            phone_number="8822222222",
            password=VALID_PASSWORD,
            is_staff=True,
        )
        self.url = "/api/auth/leave-requests/"

    def test_player_can_submit_and_list_own_leave_requests(self):
        self.client.force_authenticate(user=self.player_user)

        create_response = self.client.post(
            self.url,
            {
                "start_date": "2025-04-01",
                "end_date": "2025-04-15",
                "reason": "Out of station",
            },
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data["status"], "pending")
        self.assertEqual(create_response.data["player_id"], self.player.id)

        list_response = self.client.get(self.url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(list_response.data[0]["reason"], "Out of station")

    def test_admin_can_approve_leave_request_and_apply_membership_leave(self):
        leave_request = LeaveRequest.objects.create(
            player=self.player,
            start_date=date(2025, 4, 1),
            end_date=date(2025, 4, 15),
            reason="Medical leave",
        )
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            f"/api/auth/leave-requests/{leave_request.id}/approve/",
            {"review_note": "Approved"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        leave_request.refresh_from_db()
        self.assertEqual(leave_request.status, LeaveRequest.STATUS_APPROVED)
        self.assertEqual(leave_request.reviewed_by, self.admin_user)
        self.assertIsNotNone(leave_request.applied_leave)
        self.assertTrue(
            MembershipLeave.objects.filter(
                membership=self.player.membership,
                start_date=date(2025, 4, 1),
                end_date=date(2025, 4, 15),
            ).exists()
        )

    def test_admin_can_reject_leave_request(self):
        leave_request = LeaveRequest.objects.create(
            player=self.player,
            start_date=date(2025, 5, 1),
            end_date=date(2025, 5, 10),
            reason="Travel",
        )
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            f"/api/auth/leave-requests/{leave_request.id}/reject/",
            {"review_note": "Not enough detail"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        leave_request.refresh_from_db()
        self.assertEqual(leave_request.status, LeaveRequest.STATUS_REJECTED)
        self.assertEqual(leave_request.reviewed_by, self.admin_user)
        self.assertIsNone(leave_request.applied_leave)

    def test_admin_list_shows_all_leave_requests(self):
        LeaveRequest.objects.create(
            player=self.player,
            start_date=date(2025, 6, 1),
            end_date=date(2025, 6, 5),
            reason="Family event",
        )
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
