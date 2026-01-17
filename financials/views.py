import base64
import json
import uuid
from datetime import date

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from .models import Transaction
from .serializers import TransactionSerializer, InitiatePaymentSerializer, PaymentCallbackSerializer
from .phonepe_utils import initiate_phonepe_payment, check_payment_status


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Transaction.objects.all()

        if user.is_staff or user.is_superuser:
            player_id = self.request.query_params.get('player_id')
            if player_id:
                try:
                    player_id = int(player_id)
                except (TypeError, ValueError):
                    return Transaction.objects.none()
                return queryset.filter(player_id=player_id)
            return queryset

        try:
            player = user.player
        except ObjectDoesNotExist:
            return Transaction.objects.none()

        return queryset.filter(player=player)


class InitiatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=InitiatePaymentSerializer, responses={200: None})
    def post(self, request):
        serializer = InitiatePaymentSerializer(data=request.data)
        if not serializer.is_valid():
             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        transaction_id = serializer.validated_data['transaction_id']
        transaction = get_object_or_404(Transaction, id=transaction_id)

        if not hasattr(request.user, 'player') or transaction.player != request.user.player:
            return Response({"error": "You do not have permission to pay for this transaction"}, status=status.HTTP_403_FORBIDDEN)

        if transaction.paid:
            return Response({"message": "Transaction already paid"}, status=status.HTTP_400_BAD_REQUEST)

        merchant_transaction_id = f"TXN{transaction.id}_{str(uuid.uuid4())[:8]}"

        try:
            response = initiate_phonepe_payment(
                transaction_id=merchant_transaction_id,
                amount=transaction.amount,
                user_id=request.user.id
            )
            return Response({
                "payment_url": response.redirect_url, 
                "merchant_transaction_id": merchant_transaction_id
            })
        except Exception as e:
             return Response({"error": "Payment initiation failed", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentCallbackView(APIView):
    permission_classes = [AllowAny] 

    @extend_schema(request=PaymentCallbackSerializer, responses={200: None})
    def post(self, request):
        # Merge POST data (Form) and Body data (JSON) to check everything
        incoming_data = request.data.copy() if request.data else {}
        if request.POST:
            incoming_data.update(request.POST.dict())

        # --- DEBUG PRINT ---
        print(f"Incoming Callback Data: {incoming_data}")
        # -------------------

        merchant_transaction_id = None

        # STRATEGY 1: Check for Base64 'response' (PhonePe Webhook standard)
        if 'response' in incoming_data:
            try:
                decoded = base64.b64decode(incoming_data['response']).decode('utf-8')
                json_data = json.loads(decoded)
                merchant_transaction_id = json_data.get('data', {}).get('merchantTransactionId')
            except Exception:
                print("Failed to decode Base64 response, checking other fields...")

        # STRATEGY 2: Check for direct ID (Postman / Browser Redirect)
        if not merchant_transaction_id:
            # Check common keys used in redirects or manual testing
            merchant_transaction_id = (
                incoming_data.get('merchantTransactionId') or 
                incoming_data.get('transactionId') or
                incoming_data.get('id')
            )

        if not merchant_transaction_id:
            return Response({
                "error": "Invalid callback data", 
                "details": "No merchantTransactionId found in request. Send {'merchantTransactionId': '...'}"
            }, status=status.HTTP_400_BAD_REQUEST)

        # --- VERIFICATION ---
        try:
            # Verify status with PhonePe Server
            status_response = check_payment_status(merchant_transaction_id)

            if not status_response:
                 return Response({"status": "pending", "message": "Could not fetch status from PhonePe"})

            if status_response.state == "COMPLETED":
                try:
                    # Parse "TXN{id}_{uuid}"
                    txn_prefix = merchant_transaction_id.split('_')[0] 
                    txn_id = txn_prefix.replace("TXN", "") 
                    
                    transaction = Transaction.objects.get(id=txn_id)
                    
                    if not transaction.paid:
                        transaction.paid = True
                        transaction.payment_date = date.today()
                        transaction.save()
                        
                    return Response({"status": "success", "message": "Payment verified and updated"})
                
                except (IndexError, ValueError, Transaction.DoesNotExist):
                    return Response({"error": "Transaction not found for this ID"}, status=status.HTTP_404_NOT_FOUND)

            elif status_response.state == "FAILED":
                return Response({"status": "failed", "message": "Payment failed"}, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({"status": "pending", "message": f"Payment is {status_response.state}"})

        except Exception as e:
             return Response({"error": f"Error processing callback: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
