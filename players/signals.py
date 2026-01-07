from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Player, Membership, Subscription
from financials.models import Transaction
import datetime

@receiver(post_save, sender=Player)
def handle_new_player_creation(sender, instance, created, **kwargs):
    """
    Automates the onboarding process for new players by:
    1. Creating a Membership record.
    2. Creating a Subscription record.
    3. Generating a Transaction for the one-time registration fee.
    """
    if created:
        # Create a new membership for the player
        Membership.objects.create(
            player=instance,
            join_date=datetime.date.today(),
            status='pending'
        )

        # Create a subscription for the player
        Subscription.objects.create(player=instance)

        # Create a one-time fee transaction
        Transaction.objects.create(
            player=instance,
            category='registration',
            amount=2000.00,
            due_date=datetime.date.today(),
            paid=True,
            payment_date=datetime.date.today()
        )
