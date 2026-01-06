from django.test import TestCase
from .models import Transaction
import datetime

class TransactionModelTest(TestCase):

    def setUp(self):
        self.transaction = Transaction.objects.create(
            date=datetime.date.today(),
            amount=100.00,
            type="income",
            description="Test income"
        )

    def test_transaction_creation(self):
        transaction = Transaction.objects.get(description="Test income")
        self.assertEqual(transaction.amount, 100.00)
        self.assertEqual(transaction.type, "income")
        self.assertEqual(str(transaction), f"income of 100.00 on {datetime.date.today()}")
