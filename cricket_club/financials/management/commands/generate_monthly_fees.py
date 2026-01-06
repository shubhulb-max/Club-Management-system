from django.core.management.base import BaseCommand
from django.conf import settings
from players.models import Membership
from financials.models import Transaction
from datetime import date
from dateutil.relativedelta import relativedelta
from django.db import models

class Command(BaseCommand):
    help = 'Generates monthly fee transactions for active members who are due for payment.'

    def handle(self, *args, **options):
        today = date.today()
        one_month_ago = today - relativedelta(months=1)

        # Find all active members whose last payment was over a month ago,
        # or who have never made a payment and joined over a month ago.
        due_memberships = Membership.objects.filter(
            status='active'
        ).filter(
            models.Q(last_payment_date__lte=one_month_ago) |
            models.Q(last_payment_date__isnull=True, join_date__lte=one_month_ago)
        )

        if not due_memberships.exists():
            self.stdout.write(self.style.SUCCESS('No members are due for payment.'))
            return

        self.stdout.write(f'Found {due_memberships.count()} members due for payment. Generating fees...')

        for membership in due_memberships:
            # Create a new transaction for the monthly fee
            Transaction.objects.create(
                player=membership.player,
                date=today,
                amount=settings.MONTHLY_FEE,
                type='income',
                description=f'Monthly membership fee for {today.strftime("%B %Y")}'
            )

            # Update the last payment date on the membership
            membership.last_payment_date = today
            membership.save()

            self.stdout.write(self.style.SUCCESS(
                f'Successfully generated fee for {membership.player}.'
            ))

        self.stdout.write(self.style.SUCCESS('Finished generating monthly fees.'))
