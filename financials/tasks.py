from celery import shared_task
from django.utils import timezone

from .services import generate_monthly_invoices


@shared_task
def generate_monthly_fees_task():
    billing_date = timezone.localdate()
    result = generate_monthly_invoices(billing_date=billing_date)
    return {
        "billing_date": billing_date.isoformat(),
        "created": result.created_count,
        "billable": result.billable_players,
        "skipped_existing": result.skipped_existing,
    }
