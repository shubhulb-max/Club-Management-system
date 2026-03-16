from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image
from .models import InventoryItem, Sale, ItemAssignment
from .serializers import InventoryCategorySerializer
from players.models import Player
from teams.models import Team
from financials.models import Transaction
from datetime import date

class InventoryItemModelTest(TestCase):
    def test_inventory_item_creation(self):
        item = InventoryItem.objects.create(
            name='Club T-Shirt',
            description='Official club merchandise',
            quantity=50,
            price=25.00,
            type='merchandise'
        )
        self.assertEqual(str(item), 'Club T-Shirt')

class SaleModelTest(TestCase):
    def setUp(self):
        self.player = Player.objects.create(first_name='Sale', last_name='Test', age=25, role='batsman')
        self.item = InventoryItem.objects.create(
            name='Cricket Bat',
            description='High-quality bat',
            quantity=10,
            price=150.00,
            type='merchandise'
        )

    def test_sale_creates_transaction(self):
        sale = Sale.objects.create(
            item=self.item,
            player=self.player,
            quantity_sold=1,
            sale_date=date.today()
        )

        # Check if a transaction was created
        self.assertTrue(
            Transaction.objects.filter(
                player=self.player,
                amount=150.00,
                category='merchandise'
            ).exists()
        )

class ItemAssignmentModelTest(TestCase):
    def setUp(self):
        self.team = Team.objects.create(name='Test Team')
        self.item = InventoryItem.objects.create(
            name='Team Helmet',
            description='Safety helmet for team use',
            quantity=15,
            type='team_kit'
        )

    def test_item_assignment(self):
        assignment = ItemAssignment.objects.create(
            item=self.item,
            team=self.team,
            quantity_assigned=5,
            date_assigned=date.today()
        )
        self.assertEqual(str(assignment), '5 x Team Helmet assigned to Test Team')


class InventoryCategoryImageValidationTest(TestCase):
    def _build_test_image(self):
        buffer = BytesIO()
        image = Image.new("RGB", (20, 20), color="green")
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return SimpleUploadedFile("category.png", buffer.getvalue(), content_type="image/png")

    def test_rejects_fake_category_image(self):
        serializer = InventoryCategorySerializer(
            data={
                "name": "Bats",
                "description": "Category",
                "image": SimpleUploadedFile("category.png", b"bad image data", content_type="image/png"),
            }
        )
        self.assertFalse(serializer.is_valid())
        self.assertIn("image", serializer.errors)

    def test_accepts_valid_category_image(self):
        serializer = InventoryCategorySerializer(
            data={
                "name": "Pads",
                "description": "Category",
                "image": self._build_test_image(),
            }
        )
        self.assertTrue(serializer.is_valid(), serializer.errors)
