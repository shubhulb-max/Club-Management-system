from django.test import TestCase
from django.core.management import call_command
from django.conf import settings
from players.models import Player, Membership
from financials.models import Transaction
from datetime import date
from dateutil.relativedelta import relativedelta

class GenerateMonthlyFeesTest(TestCase):

    def setUp(self):
        # Create players with different membership statuses and payment dates
        self.active_due_player = Player.objects.create(first_name='Active', last_name='Due', age=25, role='batsman')
        Membership.objects.filter(player=self.active_due_player).update(
            status='active',
            join_date=date.today() - relativedelta(months=2),
            last_payment_date=date.today() - relativedelta(months=1, days=1) # Paid just over a month ago
        )

        self.active_paid_player = Player.objects.create(first_name='Active', last_name='Paid', age=28, role='bowler')
        Membership.objects.filter(player=self.active_paid_player).update(
            status='active',
            last_payment_date=date.today()
        )

        self.inactive_player = Player.objects.create(first_name='Inactive', last_name='Player', age=30, role='all_rounder')
        Membership.objects.filter(player=self.inactive_player).update(status='inactive')

    def test_generate_monthly_fees_command(self):
        # Run the management command
        call_command('generate_monthly_fees')

        # Check that a new transaction was created for the due player
        self.assertTrue(
            Transaction.objects.filter(
                player=self.active_due_player,
                amount=settings.MONTHLY_FEE,
                description=f'Monthly membership fee for {date.today().strftime("%B %Y")}'
            ).exists()
        )

        # Check that the due player's last payment date was updated
        self.active_due_player.membership.refresh_from_db()
        self.assertEqual(self.active_due_player.membership.last_payment_date, date.today())

        # Check that no new transaction was created for the paid player
        # We need to check count because the initial fee is also a transaction
        self.assertEqual(Transaction.objects.filter(player=self.active_paid_player).count(), 1)


        # Check that no new transaction was created for the inactive player
        self.assertEqual(Transaction.objects.filter(player=self.inactive_player).count(), 1)
