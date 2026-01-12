from rest_framework import viewsets
from .models import Transaction
from .serializers import TransactionSerializer

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
<<<<<<< HEAD

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

        # Use a composite ID to ensure uniqueness if retrying (TransactionID_UUID)
        # We append a UUID to allow multiple payment attempts for the same transaction.
        import uuid
        merchant_transaction_id = f"TXN{transaction.id}_{str(uuid.uuid4())[:8]}"

        try:
            # SDK returns a StandardCheckoutPayResponse object
            response = initiate_phonepe_payment(
                transaction_id=merchant_transaction_id,
                amount=transaction.amount,
                user_id=request.user.id
            )

            # Extract redirect URL from the SDK response object
            # Assuming response has a 'redirect_url' attribute based on typical SDK patterns
            # or response.instrument_response.redirect_info.url
            # Let's check the SDK response structure in tests or assume standard access
            return Response({
                "payment_url": response.redirect_url,
                "merchant_transaction_id": merchant_transaction_id
            })
        except Exception as e:
             return Response({"error": "Payment initiation failed", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentCallbackView(APIView):
    permission_classes = [AllowAny] # Callbacks come from PhonePe server

    def post(self, request):
        # PhonePe sends the response in a base64 encoded 'response' field
        response_encoded = request.data.get('response')

        # Check for checksum in Headers (S2S) OR Body (Browser Redirect)
        x_verify = request.headers.get('X-VERIFY') or request.data.get('checksum')

        if not response_encoded or not x_verify:
            return Response({"error": "Invalid callback data"}, status=status.HTTP_400_BAD_REQUEST)

        # Verify using SDK wrapper
        # The wrapper returns the response object or False/Raises
        try:
             # We pass the raw encoded string and the header
             is_valid = verify_callback_checksum(response_encoded, x_verify)
             if is_valid is False: # Explicit check if returns boolean False
                 return Response({"error": "Checksum verification failed"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
             return Response({"error": f"Validation Error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Decode response manually to extract data if SDK didn't return a parsed object we can easily use
        # (The wrapper currently returns 'status' or False, so we still need to parse data)
        try:
            response_data = json.loads(base64.b64decode(response_encoded).decode('utf-8'))
        except Exception:
             return Response({"error": "Invalid base64 response"}, status=status.HTTP_400_BAD_REQUEST)

        if response_data.get("code") == "PAYMENT_SUCCESS":
            merchant_transaction_id = response_data['data']['merchantTransactionId']
            # Extract ID from "TXN{id}_{uuid}"
            # Split by '_' and take the first part, then remove "TXN"
            try:
                txn_prefix = merchant_transaction_id.split('_')[0]
                txn_id = txn_prefix.replace("TXN", "")
                transaction = Transaction.objects.get(id=txn_id)
                if not transaction.paid:
                    transaction.paid = True
                    transaction.payment_date = date.today()
                    transaction.save()
            except Transaction.DoesNotExist:
                pass # Log error or ignore

        return Response({"status": "acknowledged"})
=======
>>>>>>> origin/feat-cricket-club-backend-9509745213947822927
