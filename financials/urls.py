from django.urls import path
from .views import InitiatePaymentView, PaymentCallbackView

urlpatterns = [
    path('initiate-payment/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('payment-callback/', PaymentCallbackView.as_view(), name='payment-callback'),
]
