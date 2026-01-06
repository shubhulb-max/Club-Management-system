from django.urls import path
from .views import TransactionListView, TransactionDetailView

urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction_list'),
    path('<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),
]
