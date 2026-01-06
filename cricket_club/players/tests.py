from django.test import TestCase
from .models import Player, Membership
import datetime

class PlayerModelTest(TestCase):

    def setUp(self):
        Player.objects.create(
            first_name="John",
            last_name="Doe",
            age=25,
            role="batsman",
            phone_number="1234567890"
        )

    def test_player_creation(self):
        player = Player.objects.get(first_name="John")
        self.assertEqual(player.last_name, "Doe")
        self.assertEqual(player.age, 25)
        self.assertEqual(player.role, "batsman")
        self.assertEqual(player.phone_number, "1234567890")
        self.assertEqual(str(player), "John Doe")


class MembershipModelTest(TestCase):

    def setUp(self):
        self.player = Player.objects.create(first_name="Jane", last_name="Smith", age=22, role="bowler")
        self.membership = Membership.objects.create(
            player=self.player,
            join_date=datetime.date.today(),
            status="active"
        )

    def test_membership_creation(self):
        membership = Membership.objects.get(player=self.player)
        self.assertEqual(membership.status, "active")
        self.assertEqual(membership.join_date, datetime.date.today())
        self.assertEqual(str(membership), "Jane Smith's Membership")
