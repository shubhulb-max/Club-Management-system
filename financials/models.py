from django.db import models
from players.models import Player
from datetime import date


class MembershipFeeSchedule(models.Model):
    effective_from = models.DateField(unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["-effective_from"]

    def __str__(self):
        return f"{self.amount} from {self.effective_from.isoformat()}"


class Transaction(models.Model):
    CATEGORY_CHOICES = [
        ('registration', 'Registration Fee'),
        ('monthly', 'Monthly Fee'),
        ('tournament', 'Tournament Fee'),
        ('merchandise', 'Merchandise'),
        ('fine', 'Fine/Penalty'),
    ]

    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='transactions')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='merchandise')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField(default=date.today)
    paid = models.BooleanField(default=False)
    payment_date = models.DateField(null=True, blank=True)
    waived = models.BooleanField(default=False)
    waived_reason = models.CharField(max_length=255, blank=True)

    def __str__(self):
        if self.waived:
            status = "Waived"
        else:
            status = "Paid" if self.paid else "Unpaid"
        return f"{self.get_category_display()} for {self.player} ({status})"
