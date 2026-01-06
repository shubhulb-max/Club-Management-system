from django.contrib import admin
from .models import Transaction

class TransactionAdmin(admin.ModelAdmin):
    list_display = ('date', 'player', 'type', 'amount', 'description')
    search_fields = ['player__first_name', 'player__last_name', 'description']
    list_filter = ('type', 'date')

admin.site.register(Transaction, TransactionAdmin)
