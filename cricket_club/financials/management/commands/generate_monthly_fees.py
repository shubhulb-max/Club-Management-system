from django.core.management.base import BaseCommand
from players.models import Player
from financials.models import Transaction
from datetime import date

class Command(BaseCommand):
    help = 'Generates monthly fee transactions for all active members.'

    def handle(self, *args, **options):
        today = date.today()

        # Get all players
        players = Player.objects.all()

        billable_players = [p for p in players if p.membership_active]

        if not billable_players:
            self.stdout.write(self.style.SUCCESS('No billable players found.'))
            return

        self.stdout.write(f'Found {len(billable_players)} billable players. Generating invoices...')

        for player in billable_players:
            # Check if a monthly fee has already been created for the current month
            if not Transaction.objects.filter(
                player=player,
                category='monthly',
                due_date__month=today.month,
                due_date__year=today.year
            ).exists():
                Transaction.objects.create(
                    player=player,
                    category='monthly',
                    amount=player.subscription.monthly_rate,
                    due_date=today,
                    paid=False
                )

                self.stdout.write(self.style.SUCCESS(
                    f'Successfully generated invoice for {player}.'
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    f'Invoice already exists for {player} for this month.'
                ))

        self.stdout.write(self.style.SUCCESS('Finished generating monthly invoices.'))
