from django.db import models
from players.models import Player
from datetime import date

class Transaction(models.Model):
    CATEGORY_CHOICES = [
        ('registration', 'Registration Fee'),
        ('monthly', 'Monthly Fee'),
        ('tournament', 'Tournament Fee'),
        ('merchandise', 'Merchandise'),
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transactions')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='merchandise')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(default=date.today)
    paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        status = "Paid" if self.paid else "Unpaid"
        return f"{self.get_category_display()} for {self.player} ({status})"
