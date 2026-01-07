from django.contrib import admin
from .models import Transaction

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('player', 'category', 'amount', 'due_date', 'paid', 'payment_date')
    search_fields = ['player__first_name', 'player__last_name']
    list_filter = ('category', 'paid', 'due_date')

admin.site.register(Transaction, TransactionAdmin)
