from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from players.models import Player

User = get_user_model()


@receiver(post_save, sender=User)
def link_user_to_player_by_phone(sender, instance, created, **kwargs):
    if not created:
        return
    phone_number = getattr(instance, "phone_number", None)
    if not phone_number:
        return
    players = Player.objects.filter(phone_number=phone_number)
    if players.count() != 1:
        return
    player = players.first()
    if player.user_id:
        return
    player.user = instance
    player.save(update_fields=["user"])
