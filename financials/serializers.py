from rest_framework import serializers
from .models import Transaction

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'player', 'category', 'amount', 'due_date', 'paid', 'payment_date']
