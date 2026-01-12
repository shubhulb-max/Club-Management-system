from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Transaction
from .serializers import TransactionSerializer
from .phonepe_utils import initiate_phonepe_payment, verify_callback_checksum
import base64
import json
from datetime import date

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer

class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        transaction_id = request.data.get('transaction_id')
        if not transaction_id:
            return Response({"error": "transaction_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        transaction = get_object_or_404(Transaction, id=transaction_id)

        # Ensure the user owns this transaction (via Player)
        if not hasattr(request.user, 'player') or transaction.player != request.user.player:
            return Response({"error": "You do not have permission to pay for this transaction"}, status=status.HTTP_403_FORBIDDEN)

        if transaction.paid:
            return Response({"message": "Transaction already paid"}, status=status.HTTP_400_BAD_REQUEST)

        # Use a composite ID to ensure uniqueness if retrying (TransactionID_Timestamp)
        # But for simplicity, we'll try to use the ID. PhonePe checks for unique MerchantTransactionId.
        # Ideally, we should have a separate Order model, but we'll use "TXN-{id}" format.
        merchant_transaction_id = f"TXN{transaction.id}"

        response = initiate_phonepe_payment(
            transaction_id=merchant_transaction_id,
            amount=transaction.amount,
            user_id=request.user.id,
            mobile_number=request.user.player.phone_number
        )

        if response.get("success"):
            return Response({
                "payment_url": response["data"]["instrumentResponse"]["redirectInfo"]["url"],
                "merchant_transaction_id": merchant_transaction_id
            })
        else:
            return Response({"error": "Payment initiation failed", "details": response}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentCallbackView(APIView):
    permission_classes = [AllowAny] # Callbacks come from PhonePe server

    def post(self, request):
        # PhonePe sends the response in a base64 encoded 'response' field
        response_encoded = request.data.get('response')
        x_verify = request.headers.get('X-VERIFY')

        if not response_encoded or not x_verify:
            return Response({"error": "Invalid callback data"}, status=status.HTTP_400_BAD_REQUEST)

        config = settings.PHONEPE_CONFIG

        if not verify_callback_checksum(response_encoded, x_verify, config['SALT_KEY'], config['SALT_INDEX']):
             return Response({"error": "Checksum verification failed"}, status=status.HTTP_400_BAD_REQUEST)

        # Decode response
        try:
            response_data = json.loads(base64.b64decode(response_encoded).decode('utf-8'))
        except Exception:
             return Response({"error": "Invalid base64 response"}, status=status.HTTP_400_BAD_REQUEST)

        if response_data.get("success") and response_data.get("code") == "PAYMENT_SUCCESS":
            merchant_transaction_id = response_data['data']['merchantTransactionId']
            # Extract ID from "TXN{id}"
            txn_id = merchant_transaction_id.replace("TXN", "")

            try:
                transaction = Transaction.objects.get(id=txn_id)
                if not transaction.paid:
                    transaction.paid = True
                    transaction.payment_date = date.today()
                    transaction.save()
            except Transaction.DoesNotExist:
                pass # Log error or ignore

        return Response({"status": "acknowledged"})
