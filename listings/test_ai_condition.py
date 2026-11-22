import io
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from PIL import Image
from rest_framework.test import APITestCase

from .ai_condition import price_range


def make_image(name="photo.jpg"):
    buf = io.BytesIO()
    Image.new("RGB", (20, 20), "white").save(buf, "JPEG")
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/jpeg")


class EstimateTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="pass12345")
        self.url = reverse("ai-estimate")

    def post(self, images, **extra):
        data = {"title": "Data Structures", "author": "Tanenbaum", "images": images}
        data.update(extra)
        return self.client.post(self.url, data, format="multipart")

    def test_price_rule(self):
        self.assertEqual(price_range(400, "good"), (180, 220))

    def test_login_required(self):
        self.assertIn(self.post([make_image()]).status_code, (401, 403))

    @patch("listings.ai_condition_views.estimate_condition", return_value=("good", ["Cover creased"]))
    def test_estimate_with_price(self, mock_ai):
        self.client.force_authenticate(self.user)
        response = self.post([make_image(), make_image()], original_price="400")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["suggested_condition"], "good")
        self.assertEqual(response.data["price_range"], {"low": 180, "high": 220})

    def test_no_images_rejected(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(
            self.url, {"title": "T", "author": "A"}, format="multipart"
        )
        self.assertEqual(response.status_code, 400)

    def test_five_images_rejected(self):
        self.client.force_authenticate(self.user)
        response = self.post([make_image(f"{i}.jpg") for i in range(5)])
        self.assertEqual(response.status_code, 400)

    def test_fake_image_rejected(self):
        self.client.force_authenticate(self.user)
        fake = SimpleUploadedFile("evil.jpg", b"not an image", content_type="image/jpeg")
        self.assertEqual(self.post([fake]).status_code, 400)