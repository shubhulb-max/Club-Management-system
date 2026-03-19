from calendar import monthrange
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterable, List, Optional

from django.db import transaction
from django.utils import timezone

from players.models import Player

from .models import MembershipFeeSchedule, Transaction

DEFAULT_MONTHLY_INVOICE_AMOUNT = Decimal("1050.00")


@dataclass
class BillingResult:
    created_invoices: List[Transaction]
    billable_players: int
    skipped_existing: int
    due_date: date

    @property
    def created_count(self) -> int:
        return len(self.created_invoices)


@dataclass
class BackfillResult:
    created_transactions: List[Transaction]
    skipped_existing: int
    skipped_leave_months: int
    skipped_before_join: int

    @property
    def created_count(self) -> int:
        return len(self.created_transactions)


def _players_queryset(players: Optional[Iterable[Player]] = None):
    if players is not None:
        return players
    return Player.objects.select_related("subscription", "membership").all()


def _invoice_exists(player: Player, billing_date: date) -> bool:
    return Transaction.objects.filter(
        player=player,
        category="monthly",
        due_date__year=billing_date.year,
        due_date__month=billing_date.month,
    ).exists()


def _monthly_due_date(billing_date: date) -> date:
    return billing_date.replace(day=10)


def _month_start(value: date) -> date:
    return value.replace(day=1)


def _month_end(value: date) -> date:
    return value.replace(day=monthrange(value.year, value.month)[1])


def _next_month(value: date) -> date:
    if value.month == 12:
        return value.replace(year=value.year + 1, month=1, day=1)
    return value.replace(month=value.month + 1, day=1)


def _month_iter(start_month: date, end_month: date):
    current = _month_start(start_month)
    end = _month_start(end_month)
    while current <= end:
        yield current
        current = _next_month(current)


def get_monthly_invoice_amount(billing_date: date) -> Decimal:
    schedule = (
        MembershipFeeSchedule.objects.filter(effective_from__lte=billing_date)
        .order_by("-effective_from")
        .first()
    )
    if schedule:
        return schedule.amount
    return DEFAULT_MONTHLY_INVOICE_AMOUNT


def _should_bill_player_for_month(player: Player, billing_date: date, *, require_current_active=True) -> bool:
    subscription = getattr(player, "subscription", None)
    membership = getattr(player, "membership", None)
    if subscription is None or membership is None:
        return False
    if membership.join_date > billing_date:
        return False
    if membership.fee_exempt or membership.is_on_leave_for_month(billing_date):
        return False
    if require_current_active:
        player.sync_membership_status(as_of=billing_date)
        if membership.status != "active" or not player.membership_active:
            return False
    return True


@transaction.atomic
def generate_monthly_invoices(
    *,
    billing_date: Optional[date] = None,
    players: Optional[Iterable[Player]] = None,
) -> BillingResult:
    billing_date = billing_date or timezone.localdate()
    due_date = _monthly_due_date(billing_date)
    monthly_amount = get_monthly_invoice_amount(billing_date)
    created_invoices: List[Transaction] = []
    billable_players = 0
    skipped_existing = 0

    for player in _players_queryset(players):
        if not _should_bill_player_for_month(player, billing_date):
            continue

        billable_players += 1

        if _invoice_exists(player, billing_date):
            skipped_existing += 1
            continue

        invoice = Transaction.objects.create(
            player=player,
            category="monthly",
            amount=monthly_amount,
            due_date=due_date,
            paid=False,
        )
        created_invoices.append(invoice)

    return BillingResult(
        created_invoices=created_invoices,
        billable_players=billable_players,
        skipped_existing=skipped_existing,
        due_date=due_date,
    )


@transaction.atomic
def backfill_monthly_payments(
    *,
    player: Player,
    start_month: date,
    end_month: date,
    payment_date: Optional[date] = None,
) -> BackfillResult:
    start_month = _month_start(start_month)
    end_month = _month_start(end_month)
    if end_month < start_month:
        raise ValueError("end_month must be on or after start_month")

    created_transactions: List[Transaction] = []
    skipped_existing = 0
    skipped_leave_months = 0
    skipped_before_join = 0
    membership = getattr(player, "membership", None)
    if membership is None or getattr(player, "subscription", None) is None:
        return BackfillResult(created_transactions, 0, 0, 0)

    for billing_date in _month_iter(start_month, end_month):
        if membership.join_date > billing_date:
            skipped_before_join += 1
            continue
        if membership.fee_exempt or membership.is_on_leave_for_month(billing_date):
            skipped_leave_months += 1
            continue
        if _invoice_exists(player, billing_date):
            skipped_existing += 1
            continue

        due_date = _monthly_due_date(billing_date)
        transaction_date = payment_date or due_date
        invoice = Transaction.objects.create(
            player=player,
            category="monthly",
            amount=get_monthly_invoice_amount(billing_date),
            due_date=due_date,
            paid=True,
            payment_date=transaction_date,
        )
        created_transactions.append(invoice)

    player.sync_membership_status(as_of=_month_end(end_month))
    return BackfillResult(
        created_transactions=created_transactions,
        skipped_existing=skipped_existing,
        skipped_leave_months=skipped_leave_months,
        skipped_before_join=skipped_before_join,
    )
