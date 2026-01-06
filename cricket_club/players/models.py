from django.db import models

class Player(models.Model):
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
    last_payment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.player}'s Membership"
