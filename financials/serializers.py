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


class BackfillMonthlyPaymentsSerializer(serializers.Serializer):
    player_id = serializers.IntegerField(required=True)
    start_month = serializers.DateField(required=True, help_text="Any date inside the first month to backfill.")
    end_month = serializers.DateField(required=True, help_text="Any date inside the last month to backfill.")
    payment_date = serializers.DateField(required=False, help_text="Optional payment date to apply to created records.")

    def validate(self, attrs):
        if attrs["end_month"] < attrs["start_month"]:
            raise serializers.ValidationError({"end_month": "End month must be on or after start month."})
        return attrs
