from django.test import TestCase
from .models import Player

class PlayerModelTest(TestCase):

    def setUp(self):
        Player.objects.create(
            first_name="John",
            last_name="Doe",
            age=25,
            role="batsman"
        )

    def test_player_creation(self):
        player = Player.objects.get(first_name="John")
        self.assertEqual(player.last_name, "Doe")
        self.assertEqual(player.age, 25)
        self.assertEqual(player.role, "batsman")
        self.assertEqual(str(player), "John Doe")
