from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Sale
from financials.models import Transaction

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
