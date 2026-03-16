from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image
from .models import Team
from players.models import Player
from .serializers import TeamSerializer

class TeamModelTest(TestCase):

    def setUp(self):
        self.captain = Player.objects.create(first_name="Team", last_name="Captain", age=30, role="all_rounder")
        self.player = Player.objects.create(first_name="Test", last_name="Player", age=28, role="bowler")
        self.team = Team.objects.create(name="Test Team", captain=self.captain)
        self.team.players.add(self.player)

    def test_team_creation(self):
        team = Team.objects.get(name="Test Team")
        self.assertEqual(team.captain.first_name, "Team")
        self.assertEqual(team.players.count(), 1)
        self.assertEqual(team.players.first().first_name, "Test")
        self.assertEqual(str(team), "Test Team")


class TeamLogoValidationTest(TestCase):
    def _build_test_image(self):
        buffer = BytesIO()
        image = Image.new("RGB", (20, 20), color="blue")
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return SimpleUploadedFile("logo.png", buffer.getvalue(), content_type="image/png")

    def test_rejects_fake_team_logo(self):
        serializer = TeamSerializer(
            data={
                "name": "Logo Team",
                "captain": self._build_captain().id,
                "player_ids": [],
                "logo": SimpleUploadedFile("logo.png", b"bad image data", content_type="image/png"),
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("logo", serializer.errors)

    def test_accepts_valid_team_logo(self):
        captain = self._build_captain()
        serializer = TeamSerializer(
            data={
                "name": "Valid Logo Team",
                "captain": captain.id,
                "player_ids": [],
                "logo": self._build_test_image(),
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def _build_captain(self):
        return Player.objects.create(first_name="Logo", last_name="Captain", age=29, role="all_rounder")
