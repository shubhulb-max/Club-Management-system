from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import TournamentParticipation
from financials.models import Transaction
import datetime

@receiver(post_save, sender=TournamentParticipation)
def create_tournament_fee_transaction(sender, instance, created, **kwargs):
    """
    Automatically creates a Transaction for the tournament entry fee
    when a player is added to a tournament.
    """
    if created:
        Transaction.objects.create(
            player=instance.player,
            category='tournament',
            amount=instance.tournament.entry_fee,
            due_date=datetime.date.today(),
            paid=False
        )
