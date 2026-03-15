from django.conf import settings
from django.db import models
from datetime import date, timedelta


class Player(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )

    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    age = models.PositiveIntegerField(default=0)

    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
    phone_number = models.CharField(max_length=15,unique=True, null=True, blank=True)

    ROLE_CHOICES = [
        ("batsman", "Batsman"),
        ("bowler", "Bowler"),
        ("all_rounder", "All-Rounder"),
        ("wicket_keeper", "Wicket-Keeper"),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="all_rounder")

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


    def save(self, *args, **kwargs):
        if self.user:
            if not self.first_name:
                self.first_name = self.user.first_name
            if not self.last_name:
                self.last_name = self.user.last_name
            if not self.phone_number:
                self.phone_number = self.user.phone_number

        super().save(*args, **kwargs)

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


class RegistrationRequest(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    phone_number = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    password_hash = models.CharField(max_length=128)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_registration_requests",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.phone_number} ({self.status})"
