from django.core.exceptions import ValidationError
from django.db import models
from teams.models import Team
from players.models import Player


class InventoryCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='inventory/categories/', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Inventory Categories"

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    TYPE_CHOICES = [
        ('team_kit', 'Team Kit'),
        ('merchandise', 'Merchandise'),
    ]

    category = models.ForeignKey(
        InventoryCategory,
        on_delete=models.CASCADE,
        related_name='items',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.PositiveIntegerField(default=0)
    available_quantity = models.PositiveIntegerField(default=0)
    missing_quantity = models.PositiveIntegerField(default=0)
    destroyed_quantity = models.PositiveIntegerField(default=0)
    distributed_quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True) # Price is for merchandise
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name

    def clean(self):
        super().clean()
        status_total = (
            self.available_quantity +
            self.missing_quantity +
            self.destroyed_quantity +
            self.distributed_quantity
        )

        if status_total > self.quantity:
            raise ValidationError("Sum of status quantities cannot exceed total quantity.")

    def save(self, *args, **kwargs):
        if (
            self.quantity and
            self.available_quantity == 0 and
            self.missing_quantity == 0 and
            self.destroyed_quantity == 0 and
            self.distributed_quantity == 0
        ):
            self.available_quantity = self.quantity
        self.full_clean()
        return super().save(*args, **kwargs)

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
