from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    BackfillMonthlyPaymentsView,
    GenerateMonthlyInvoicesView,
    InitiatePaymentView,
    PaymentCallbackView,
    TransactionViewSet,
)

router = DefaultRouter()
router.register(
    r"transactions", TransactionViewSet, basename="transaction"
)

urlpatterns = [
    path('generate-monthly-invoices/', GenerateMonthlyInvoicesView.as_view(), name='generate-monthly-invoices'),
    path('backfill-monthly-payments/', BackfillMonthlyPaymentsView.as_view(), name='backfill-monthly-payments'),
    path('initiate-payment/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('payment-callback/', PaymentCallbackView.as_view(), name='payment-callback'),
]
