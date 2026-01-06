from django.test import TestCase
from .models import Transaction
from players.models import Player
import datetime

class TransactionModelTest(TestCase):

    def setUp(self):
        self.player = Player.objects.create(
            first_name="Test",
            last_name="Player",
            age=30,
            role="all_rounder"
        )
        self.transaction = Transaction.objects.create(
            player=self.player,
            date=datetime.date.today(),
            amount=2000.00,
            type="income",
            description="One-time membership fee"
        )

    def test_transaction_creation(self):
        transaction = Transaction.objects.get(description="One-time membership fee")
        self.assertEqual(transaction.player.first_name, "Test")
        self.assertEqual(transaction.amount, 2000.00)
        self.assertEqual(transaction.type, "income")
        self.assertEqual(str(transaction), f"income of 2000.00 on {datetime.date.today()}")
