from django.test import TestCase
from django.core.management import call_command
from players.models import MembershipLeave, Player
from financials.models import Transaction
from financials.services import get_monthly_invoice_amount
from datetime import date, timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
import base64
import json
from unittest.mock import patch, MagicMock


class GenerateMonthlyFeesTest(TestCase):

    def setUp(self):
        self.active_player = Player.objects.create(first_name='Active', last_name='Player', age=25, role='top_order_batter')
        self.overdue_player = Player.objects.create(first_name='Overdue', last_name='Player', age=30, role='all_rounder')
        self.active_player.membership.status = "active"
        self.active_player.membership.save(update_fields=["status"])
        self.overdue_player.membership.status = "active"
        self.overdue_player.membership.save(update_fields=["status"])

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
                amount=get_monthly_invoice_amount(date.today()),
                due_date=date.today().replace(day=10),
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

class PaymentFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.user = User.objects.create_user(phone_number='9998887777', password='password')
        self.player = Player.objects.create(
            user=self.user,
            first_name="Test",
            last_name="Player",
            age=25,
            role="top_order_batter",
            phone_number="9876543210"
        )
        self.transaction = Transaction.objects.create(
            player=self.player,
            amount=500.00,
            category="monthly",
            paid=False
        )
        self.client.force_authenticate(user=self.user)
        self.initiate_url = reverse('initiate-payment')
        self.callback_url = reverse('payment-callback')

    @patch('financials.views.initiate_phonepe_payment')
    def test_initiate_payment_success(self, mock_initiate):
        # Mocking the response object from SDK
        mock_response = MagicMock()
        mock_response.redirect_url = "https://test.phonepe.com/pay"
        mock_initiate.return_value = mock_response

        response = self.client.post(self.initiate_url, {'transaction_id': self.transaction.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payment_url'], "https://test.phonepe.com/pay")
        # Check if merchant_transaction_id starts with TXN{id}_
        self.assertTrue(response.data['merchant_transaction_id'].startswith(f"TXN{self.transaction.id}_"))

    def test_initiate_payment_invalid_transaction(self):
        response = self.client.post(self.initiate_url, {'transaction_id': 9999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_initiate_payment_already_paid(self):
        self.transaction.paid = True
        self.transaction.save()

        response = self.client.post(self.initiate_url, {'transaction_id': self.transaction.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_initiate_payment_rejects_waived_transaction(self):
        self.transaction.waived = True
        self.transaction.waived_reason = "Approved leave"
        self.transaction.save(update_fields=["waived", "waived_reason"])

        response = self.client.post(self.initiate_url, {'transaction_id': self.transaction.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class GenerateMonthlyInvoicesApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        User = get_user_model()
        self.admin_user = User.objects.create_user(
            phone_number='9000000001',
            password='password',
            is_staff=True,
        )
        self.regular_user = User.objects.create_user(
            phone_number='9000000002',
            password='password',
        )
        self.active_player = Player.objects.create(
            first_name='Active',
            last_name='Member',
            age=21,
            role='top_order_batter',
            phone_number='8000000001',
        )
        self.overdue_player = Player.objects.create(
            first_name='Inactive',
            last_name='Member',
            age=22,
            role='bowler',
            phone_number='8000000002',
        )
        self.active_player.membership.status = "active"
        self.active_player.membership.save(update_fields=["status"])
        self.overdue_player.membership.status = "active"
        self.overdue_player.membership.save(update_fields=["status"])
        Transaction.objects.create(
            player=self.overdue_player,
            category='monthly',
            amount=750,
            due_date=date.today() - timedelta(days=31),
            paid=False,
        )
        self.url = reverse('generate-monthly-invoices')
        self.backfill_url = reverse('backfill-monthly-payments')

    def test_admin_can_generate_monthly_invoices(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(self.url, {'billing_date': '2026-03-01'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['billable_players'], 1)
        self.assertEqual(response.data['created_invoices'], 1)
        self.assertEqual(response.data['skipped_existing'], 0)
        self.assertEqual(response.data['billing_date'], '2026-03-01')
        self.assertEqual(response.data['due_date'], '2026-03-10')
        self.assertEqual(response.data['amount'], '1050.00')
        self.assertTrue(
            Transaction.objects.filter(
                player=self.active_player,
                category='monthly',
                amount=get_monthly_invoice_amount(date(2026, 3, 1)),
                due_date=date(2026, 3, 10),
                paid=False,
            ).exists()
        )

    def test_admin_generation_is_idempotent(self):
        self.client.force_authenticate(user=self.admin_user)

        first_response = self.client.post(self.url, {'billing_date': '2026-03-01'}, format='json')
        second_response = self.client.post(self.url, {'billing_date': '2026-03-01'}, format='json')

        self.assertEqual(first_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.status_code, status.HTTP_200_OK)
        self.assertEqual(second_response.data['created_invoices'], 0)
        self.assertEqual(second_response.data['skipped_existing'], 1)
        self.assertEqual(second_response.data['due_date'], '2026-03-10')
        self.assertEqual(second_response.data['amount'], '1050.00')
        self.assertEqual(
            Transaction.objects.filter(
                player=self.active_player,
                category='monthly',
                amount=get_monthly_invoice_amount(date(2026, 3, 1)),
                due_date=date(2026, 3, 10),
            ).count(),
            1,
        )

    def test_rate_changes_by_billing_date(self):
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(self.url, {'billing_date': '2025-03-01'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['amount'], '750.00')
        self.assertTrue(
            Transaction.objects.filter(
                player=self.active_player,
                category='monthly',
                amount=get_monthly_invoice_amount(date(2025, 3, 1)),
                due_date=date(2025, 3, 10),
                paid=False,
            ).exists()
        )

    def test_january_2026_uses_old_rate_and_february_2026_uses_new_rate(self):
        self.client.force_authenticate(user=self.admin_user)

        january_response = self.client.post(self.url, {'billing_date': '2026-01-01'}, format='json')
        february_response = self.client.post(self.url, {'billing_date': '2026-02-01'}, format='json')

        self.assertEqual(january_response.status_code, status.HTTP_200_OK)
        self.assertEqual(february_response.status_code, status.HTTP_200_OK)
        self.assertEqual(january_response.data['amount'], '750.00')
        self.assertEqual(february_response.data['amount'], '1050.00')

    def test_future_join_date_is_not_billed(self):
        self.active_player.membership.join_date = date(2026, 4, 1)
        self.active_player.membership.status = "active"
        self.active_player.membership.save(update_fields=["join_date", "status"])
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(self.url, {'billing_date': '2026-03-01'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['billable_players'], 0)
        self.assertFalse(
            Transaction.objects.filter(
                player=self.active_player,
                category='monthly',
                due_date=date(2026, 3, 10),
            ).exists()
        )

    def test_fee_exempt_player_is_not_billed(self):
        self.active_player.membership.fee_exempt = True
        self.active_player.membership.fee_exempt_reason = "Lifetime exemption"
        self.active_player.membership.save(update_fields=["fee_exempt", "fee_exempt_reason"])
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(self.url, {'billing_date': '2026-03-01'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['billable_players'], 0)
        self.assertFalse(
            Transaction.objects.filter(
                player=self.active_player,
                category='monthly',
                due_date=date(2026, 3, 10),
            ).exists()
        )

    def test_ninety_day_overdue_player_is_marked_left(self):
        Transaction.objects.create(
            player=self.active_player,
            category='monthly',
            amount=750,
            due_date=date(2025, 11, 30),
            paid=False,
        )
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(self.url, {'billing_date': '2026-03-01'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.active_player.membership.refresh_from_db()
        self.assertEqual(self.active_player.membership.status, "left")
        self.assertEqual(response.data['billable_players'], 0)

    def test_player_on_leave_is_not_billed_for_that_month(self):
        MembershipLeave.objects.create(
            membership=self.active_player.membership,
            start_date=date(2026, 3, 1),
            end_date=date(2026, 3, 31),
            reason="On leave",
        )
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(self.url, {'billing_date': '2026-03-01'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['billable_players'], 0)
        self.assertFalse(
            Transaction.objects.filter(
                player=self.active_player,
                category='monthly',
                due_date=date(2026, 3, 10),
            ).exists()
        )

    def test_waived_invoice_does_not_block_membership_status(self):
        Transaction.objects.create(
            player=self.active_player,
            category='monthly',
            amount=750,
            due_date=date(2025, 11, 30),
            paid=False,
            waived=True,
            waived_reason="Management waiver",
        )
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(self.url, {'billing_date': '2026-03-01'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.active_player.membership.refresh_from_db()
        self.assertEqual(self.active_player.membership.status, "active")

    def test_backfill_creates_paid_months_and_skips_leave(self):
        MembershipLeave.objects.create(
            membership=self.active_player.membership,
            start_date=date(2025, 2, 1),
            end_date=date(2025, 2, 28),
            reason="Absent approved leave",
        )
        self.client.force_authenticate(user=self.admin_user)

        response = self.client.post(
            self.backfill_url,
            {
                'player_id': self.active_player.id,
                'start_month': '2025-01-01',
                'end_month': '2025-03-01',
                'payment_date': '2025-03-15',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['created_transactions'], 2)
        self.assertEqual(response.data['skipped_leave_months'], 1)
        january_txn = Transaction.objects.get(player=self.active_player, category='monthly', due_date=date(2025, 1, 10))
        march_txn = Transaction.objects.get(player=self.active_player, category='monthly', due_date=date(2025, 3, 10))
        self.assertTrue(january_txn.paid)
        self.assertTrue(march_txn.paid)
        self.assertEqual(january_txn.payment_date, date(2025, 3, 15))
        self.assertFalse(
            Transaction.objects.filter(
                player=self.active_player,
                category='monthly',
                due_date=date(2025, 2, 10),
            ).exists()
        )

    def test_non_admin_cannot_generate_monthly_invoices(self):
        self.client.force_authenticate(user=self.regular_user)

        response = self.client.post(self.url, {'billing_date': '2026-03-01'}, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('financials.views.verify_callback_checksum')
    def test_payment_callback_success_s2s(self, mock_verify):
        # Test Server-to-Server callback (Header-based)
        mock_verify.return_value = True

        merchant_transaction_id = f"TXN{self.transaction.id}_abc123"
        response_data = {
            "success": True,
            "code": "PAYMENT_SUCCESS",
            "data": {
                "merchantTransactionId": merchant_transaction_id,
                "amount": 50000
            }
        }
        response_json = json.dumps(response_data)
        response_encoded = base64.b64encode(response_json.encode('utf-8')).decode('utf-8')

        self.client.logout()

        response = self.client.post(
            self.callback_url,
            {'response': response_encoded},
            **{'HTTP_X_VERIFY': "dummy_checksum"}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertTrue(self.transaction.paid)

    @patch('financials.views.verify_callback_checksum')
    def test_payment_callback_success_redirect(self, mock_verify):
        # Test Browser Redirect callback (Body-based checksum)
        mock_verify.return_value = True

        # Reset transaction
        self.transaction.paid = False
        self.transaction.save()

        merchant_transaction_id = f"TXN{self.transaction.id}_xyz789"
        response_data = {
            "success": True,
            "code": "PAYMENT_SUCCESS",
            "data": {
                "merchantTransactionId": merchant_transaction_id,
                "amount": 50000
            }
        }
        response_json = json.dumps(response_data)
        response_encoded = base64.b64encode(response_json.encode('utf-8')).decode('utf-8')

        self.client.logout()

        # Pass checksum in BODY (data)
        response = self.client.post(
            self.callback_url,
            {'response': response_encoded, 'checksum': 'dummy_checksum_body'}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.transaction.refresh_from_db()
        self.assertTrue(self.transaction.paid)

    @patch('financials.views.verify_callback_checksum')
    def test_payment_callback_invalid_checksum(self, mock_verify):
        mock_verify.return_value = False # Simulate failure

        response_encoded = "some_base64_data"
        x_verify = "invalid_checksum"

        self.client.logout()
        response = self.client.post(
            self.callback_url,
            {'response': response_encoded},
            **{'HTTP_X_VERIFY': x_verify}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
