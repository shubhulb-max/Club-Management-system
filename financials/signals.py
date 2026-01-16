from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver

from .models import Transaction
from notifications.services import notify_payment_received


@receiver(pre_save, sender=Transaction)
def cache_previous_paid_state(sender, instance, **kwargs):
    if not instance.pk:
        instance._previous_paid = False
    else:
        try:
            previous = sender.objects.get(pk=instance.pk)
            instance._previous_paid = previous.paid
        except sender.DoesNotExist:
            instance._previous_paid = False


@receiver(post_save, sender=Transaction)
def send_payment_notification(sender, instance, created, **kwargs):
    became_paid = instance.paid and (created or not getattr(instance, "_previous_paid", False))
    if became_paid:
        notify_payment_received(instance)
