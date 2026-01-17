from datetime import date
from decimal import Decimal
from typing import Optional

from django.db import transaction
from django.utils import timezone

from .models import Membership, Player, Subscription
from financials.models import Transaction

ADMISSION_FEE = Decimal("2000.00")


def _ensure_membership(player: Player, join_date):
    return Membership.objects.create(
        player=player,
        join_date=join_date,
        status="pending",
    )


def _ensure_subscription(player: Player):
    return Subscription.objects.create(player=player)


def _create_admission_invoice(player: Player, due_date, amount: Decimal):
    return Transaction.objects.create(
        player=player,
        category="registration",
        amount=amount,
        due_date=due_date,
        paid=False,
    )


@transaction.atomic
def onboard_player(
    player: Player,
    *,
    join_date: Optional[date] = None,
    admission_fee: Decimal = ADMISSION_FEE,
):
    """
    Creates a membership, subscription, and initial admission invoice for a player.
    """
    join_date = join_date or timezone.localdate()

    membership = _ensure_membership(player, join_date)
    subscription = _ensure_subscription(player)
    admission_invoice = _create_admission_invoice(player, join_date, admission_fee)

    return {
        "membership": membership,
        "subscription": subscription,
        "admission_invoice": admission_invoice,
    }
