from django.core.management.base import BaseCommand

from financials.services import generate_monthly_invoices

class Command(BaseCommand):
    help = 'Generates monthly fee transactions for all active members.'

    def handle(self, *args, **options):
        result = generate_monthly_invoices()

        if not result.billable_players:
            self.stdout.write(self.style.SUCCESS('No billable players found.'))
            return

        self.stdout.write(
            f'Found {result.billable_players} billable players. Generating invoices...'
        )

        for invoice in result.created_invoices:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully generated invoice for {invoice.player}.'
                )
            )

        if result.skipped_existing:
            self.stdout.write(
                self.style.WARNING(
                    f'Skipped {result.skipped_existing} existing monthly invoice(s).'
                )
            )

        self.stdout.write(self.style.SUCCESS('Finished generating monthly invoices.'))
