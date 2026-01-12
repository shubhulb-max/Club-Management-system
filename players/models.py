from django.db import models
from datetime import date, timedelta
from django.contrib.auth.models import User

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    ROLE_CHOICES = [
        ('batsman', 'Batsman'),
        ('bowler', 'Bowler'),
        ('all_rounder', 'All-Rounder'),
        ('wicket_keeper', 'Wicket-Keeper'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    @property
    def membership_active(self):
        """
        A player's membership is active if they have no unpaid 'Monthly Fee'
        invoices older than 30 days.
        """
        thirty_days_ago = date.today() - timedelta(days=30)
        return not self.transactions.filter(
            category='monthly',
            paid=False,
            due_date__lt=thirty_days_ago
        ).exists()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Membership(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    join_date = models.DateField()
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending'),
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"{self.player}'s Membership"

class Subscription(models.Model):
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    monthly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=750.00)
    start_date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.player}'s Subscription"
