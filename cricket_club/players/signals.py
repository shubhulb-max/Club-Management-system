from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Player, Membership
from financials.models import Transaction
import datetime

@receiver(post_save, sender=Player)
def create_player_membership_and_fee(sender, instance, created, **kwargs):
    """
    Automatically creates a Membership and a one-time fee Transaction
    when a new Player is created.
    """
    if created:
        # Create a new membership for the player
        Membership.objects.create(
            player=instance,
            join_date=datetime.date.today(),
            status='pending'
        )

        # Create a one-time fee transaction
        Transaction.objects.create(
            player=instance,
            date=datetime.date.today(),
            amount=2000.00,
            type='income',
            description=f"One-time membership fee for {instance}"
        )
