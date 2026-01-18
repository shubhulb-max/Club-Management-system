from django.test import TestCase
from django.core.management import call_command
from players.models import Player
from financials.models import Transaction
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
            role="batsman",
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
