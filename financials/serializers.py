from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'player', 'category', 'amount', 'due_date', 'paid', 'payment_date']


class InitiatePaymentSerializer(serializers.Serializer):
    transaction_id = serializers.IntegerField(required=True, help_text="The ID of the transaction to pay for.")


class PaymentCallbackSerializer(serializers.Serializer):
    response = serializers.CharField(required=True, help_text="Base64 encoded JSON response from PhonePe.")


class GenerateMonthlyInvoicesSerializer(serializers.Serializer):
    billing_date = serializers.DateField(
        required=False,
        help_text="Optional billing date for the generated monthly invoices. Defaults to today.",
    )
