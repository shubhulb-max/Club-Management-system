from django.db import models

class Transaction(models.Model):
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    TYPE_CHOICES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    description = models.TextField()

    def __str__(self):
        return f"{self.type} of {self.amount} on {self.date}"
