from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from teams.models import Team
from players.models import Player
from financials.models import Transaction

class InventoryItem(models.Model):
    TYPE_CHOICES = [
        ('team_kit', 'Team Kit'),
        ('merchandise', 'Merchandise'),
    ]

    name = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Price is for merchandise
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name

class ItemAssignment(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, limit_choices_to={'type': 'team_kit'})
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    quantity_assigned = models.PositiveIntegerField()
    date_assigned = models.DateField()

    def __str__(self):
        return f"{self.quantity_assigned} x {self.item.name} assigned to {self.team.name}"

class Sale(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, limit_choices_to={'type': 'merchandise'})
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    quantity_sold = models.PositiveIntegerField()
    sale_date = models.DateField()

    def __str__(self):
        return f"Sale of {self.quantity_sold} x {self.item.name} to {self.player}"

@receiver(post_save, sender=Sale)
def create_sale_transaction(sender, instance, created, **kwargs):
    """
    Automatically creates a Transaction when a new Sale is recorded.
    """
    if created:
        Transaction.objects.create(
            player=instance.player,
            category='merchandise',
            amount=instance.item.price * instance.quantity_sold,
            due_date=instance.sale_date,
            paid=True,
            payment_date=instance.sale_date
        )
