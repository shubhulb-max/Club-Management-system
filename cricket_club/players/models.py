from django.db import models

class Player(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.PositiveIntegerField()
    ROLE_CHOICES = [
        ('batsman', 'Batsman'),
        ('bowler', 'Bowler'),
        ('all_rounder', 'All-Rounder'),
        ('wicket_keeper', 'Wicket-Keeper'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
