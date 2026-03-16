from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from .models import Media


class MediaApprovalTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_model = get_user_model()

    def _build_test_image(self, name="photo.png"):
        buffer = BytesIO()
        image = Image.new("RGB", (20, 20), color="purple")
        image.save(buffer, format="PNG")
        buffer.seek(0)
        return SimpleUploadedFile(name, buffer.getvalue(), content_type="image/png")

    def test_uploaded_media_starts_pending_and_hidden_from_public_list(self):
        user = self.user_model.objects.create_user(phone_number="9000000001", password="password123")
        self.client.force_authenticate(user=user)

        create_response = self.client.post(
            "/api/media/",
            {
                "title": "Pending Photo",
                "media_type": "photo",
                "file": self._build_test_image(),
            },
            format="multipart",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        media = Media.objects.get(id=create_response.data["id"])
        self.assertFalse(media.is_approved)
        self.assertEqual(media.uploaded_by, user)
        self.assertEqual(create_response.data["uploaded_by"], user.id)

        self.client.force_authenticate(user=None)
        list_response = self.client.get("/api/media/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(list_response.data, [])

    def test_admin_can_approve_media(self):
        user = self.user_model.objects.create_user(phone_number="9000000002", password="password123")
        media = Media.objects.create(
            title="Pending Photo",
            media_type="photo",
            file=self._build_test_image("approve.png"),
        )

        self.client.force_authenticate(user=user)
        denied_response = self.client.post(f"/api/media/{media.id}/approve/")
        self.assertEqual(denied_response.status_code, status.HTTP_403_FORBIDDEN)

        admin = self.user_model.objects.create_user(
            phone_number="9000000003",
            password="password123",
            is_staff=True,
        )
        self.client.force_authenticate(user=admin)
        approve_response = self.client.post(f"/api/media/{media.id}/approve/")

        self.assertEqual(approve_response.status_code, status.HTTP_200_OK)
        media.refresh_from_db()
        self.assertTrue(media.is_approved)
        self.assertEqual(media.approved_by, admin)
        self.assertIsNone(media.uploaded_by)

        self.client.force_authenticate(user=None)
        list_response = self.client.get("/api/media/")
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list_response.data), 1)
        self.assertEqual(list_response.data[0]["id"], media.id)

    def test_serializer_returns_uploader_name(self):
        user = self.user_model.objects.create_user(
            phone_number="9000000004",
            password="password123",
            first_name="Shubham",
            last_name="Singh",
        )
        media = Media.objects.create(
            title="Named Upload",
            media_type="photo",
            file=self._build_test_image("named.png"),
            uploaded_by=user,
            is_approved=True,
        )

        response = self.client.get(f"/api/media/{media.id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["uploaded_by"], user.id)
        self.assertEqual(response.data["uploaded_by_name"], "Shubham Singh")
