from django.test import TestCase
from django.core.management import call_command
from players.models import Player
from financials.models import Transaction
from datetime import date, timedelta
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .phonepe_utils import generate_checksum, verify_callback_checksum
import base64
import json
import hashlib
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

class PhonePeUtilsTests(TestCase):
    def test_generate_checksum(self):
        payload = "test_payload"
        salt_key = "test_salt_key"
        salt_index = 1

        # Expected: SHA256(payload + "/pg/v1/pay" + salt_key) + "###" + salt_index
        string_to_hash = f"{payload}/pg/v1/pay{salt_key}"
        expected_hash = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()
        expected_checksum = f"{expected_hash}###{salt_index}"

        self.assertEqual(generate_checksum(payload, salt_key, salt_index), expected_checksum)

    def test_verify_callback_checksum(self):
        response_payload = "test_response_payload"
        salt_key = "test_salt_key"
        salt_index = 1

        # Calculate valid checksum
        string_to_hash = f"{response_payload}{salt_key}"
        expected_hash = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()
        valid_checksum = f"{expected_hash}###{salt_index}"

        self.assertTrue(verify_callback_checksum(response_payload, valid_checksum, salt_key, salt_index))
        self.assertFalse(verify_callback_checksum(response_payload, "invalid_checksum", salt_key, salt_index))

class PaymentFlowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password')
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
        mock_initiate.return_value = {
            "success": True,
            "data": {
                "instrumentResponse": {
                    "redirectInfo": {
                        "url": "https://test.phonepe.com/pay"
                    }
                }
            }
        }

        response = self.client.post(self.initiate_url, {'transaction_id': self.transaction.id})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['payment_url'], "https://test.phonepe.com/pay")
        self.assertEqual(response.data['merchant_transaction_id'], f"TXN{self.transaction.id}")

    def test_initiate_payment_invalid_transaction(self):
        response = self.client.post(self.initiate_url, {'transaction_id': 9999})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_initiate_payment_already_paid(self):
        self.transaction.paid = True
        self.transaction.save()

        response = self.client.post(self.initiate_url, {'transaction_id': self.transaction.id})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_payment_callback_success(self):
        # Prepare valid callback data
        merchant_transaction_id = f"TXN{self.transaction.id}"
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

        # Generate valid checksum using the config from settings (using actual settings for test)
        from django.conf import settings
        config = settings.PHONEPE_CONFIG

        string_to_hash = f"{response_encoded}{config['SALT_KEY']}"
        expected_hash = hashlib.sha256(string_to_hash.encode('utf-8')).hexdigest()
        x_verify = f"{expected_hash}###{config['SALT_INDEX']}"

        # Callback endpoint is public, so no authentication needed (or AllowAny)
        self.client.logout()

        response = self.client.post(
            self.callback_url,
            {'response': response_encoded},
            **{'HTTP_X_VERIFY': x_verify}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verify transaction is updated
        self.transaction.refresh_from_db()
        self.assertTrue(self.transaction.paid)
        self.assertIsNotNone(self.transaction.payment_date)

    def test_payment_callback_invalid_checksum(self):
        response_encoded = "some_base64_data"
        x_verify = "invalid_checksum"

        self.client.logout()
        response = self.client.post(
            self.callback_url,
            {'response': response_encoded},
            **{'HTTP_X_VERIFY': x_verify}
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
