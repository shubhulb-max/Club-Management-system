from django.views.generic import ListView, DetailView
from .models import Transaction

class TransactionListView(ListView):
    model = Transaction
    template_name = 'financials/transaction_list.html'
    context_object_name = 'transactions'

class TransactionDetailView(DetailView):
    model = Transaction
    template_name = 'financials/transaction_detail.html'
    context_object_name = 'transaction'
