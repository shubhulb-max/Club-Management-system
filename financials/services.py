from dataclasses import dataclass
from datetime import date
from typing import Iterable, List, Optional

from django.db import transaction
from django.utils import timezone

from players.models import Player

from .models import Transaction


@dataclass
class BillingResult:
    created_invoices: List[Transaction]
    billable_players: int
    skipped_existing: int

    @property
    def created_count(self) -> int:
        return len(self.created_invoices)


def _players_queryset(players: Optional[Iterable[Player]] = None):
    if players is not None:
        return players
    return Player.objects.select_related("subscription").all()


def _invoice_exists(player: Player, billing_date: date) -> bool:
    return Transaction.objects.filter(
        player=player,
        category="monthly",
        due_date__year=billing_date.year,
        due_date__month=billing_date.month,
    ).exists()


@transaction.atomic
def generate_monthly_invoices(
    *,
    billing_date: Optional[date] = None,
    players: Optional[Iterable[Player]] = None,
) -> BillingResult:
    billing_date = billing_date or timezone.localdate()
    created_invoices: List[Transaction] = []
    billable_players = 0
    skipped_existing = 0

    for player in _players_queryset(players):
        subscription = getattr(player, "subscription", None)
        if not player.membership_active or subscription is None:
            continue

        billable_players += 1

        if _invoice_exists(player, billing_date):
            skipped_existing += 1
            continue

        invoice = Transaction.objects.create(
            player=player,
            category="monthly",
            amount=subscription.monthly_rate,
            due_date=billing_date,
            paid=False,
        )
        created_invoices.append(invoice)

    return BillingResult(
        created_invoices=created_invoices,
        billable_players=billable_players,
        skipped_existing=skipped_existing,
    )
