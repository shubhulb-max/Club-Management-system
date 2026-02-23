from django.test import TestCase
from django.core.management import call_command
from players.models import Player, Membership, Subscription
from financials.models import Transaction
from io import StringIO

class ImportPlayersCommandTest(TestCase):
    def test_import_players(self):
        out = StringIO()
        call_command('import_players', stdout=out)

        # Verify 36 players created
        self.assertEqual(Player.objects.count(), 36)

        # Check specific players
        aashit = Player.objects.get(phone_number='9690009945')
        self.assertEqual(aashit.first_name, 'Aashit')
        self.assertEqual(aashit.last_name, 'Srivastava')

        imran = Player.objects.get(first_name='Imran')
        self.assertIsNone(imran.phone_number)

        # Check related records created by signals
        self.assertTrue(Membership.objects.filter(player=aashit).exists())
        self.assertTrue(Subscription.objects.filter(player=aashit).exists())
        self.assertTrue(Transaction.objects.filter(player=aashit, category='registration').exists())

        self.assertIn('Successfully created player: Aashit Srivastava', out.getvalue())
        self.assertIn('Successfully created player: Imran', out.getvalue())

    def test_import_players_idempotency(self):
        out = StringIO()
        call_command('import_players', stdout=out)
        self.assertEqual(Player.objects.count(), 36)

        # Run again
        out2 = StringIO()
        call_command('import_players', stdout=out2)

        # Count should remain 36
        self.assertEqual(Player.objects.count(), 36)
        self.assertIn('Player with phone 9690009945 already exists', out2.getvalue())
        self.assertIn('Player already exists: Imran', out2.getvalue())
