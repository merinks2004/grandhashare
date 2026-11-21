from unittest.mock import patch

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase

from .ai import AIUnavailable

PAYLOAD = {
    "title": "Data Structures",
    "author": "Tanenbaum",
    "subject": "Data Structures",
    "condition": "good",
    "course_name": "B.Tech CSE",
}


class AIDescriptionTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="pass12345")
        self.url = reverse("ai-description")

    def test_login_required(self):
        response = self.client.post(self.url, PAYLOAD)
        self.assertIn(response.status_code, (401, 403))

    @patch("listings.ai_views.generate_description", return_value="A fake description.")
    def test_returns_description(self, mock_ai):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, PAYLOAD)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["description"], "A fake description.")
        mock_ai.assert_called_once()

    @patch("listings.ai_views.generate_description", side_effect=AIUnavailable("down"))
    def test_ai_failure_gives_503(self, mock_ai):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, PAYLOAD)
        self.assertEqual(response.status_code, 503)

    def test_invalid_condition_rejected(self):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, {**PAYLOAD, "condition": "great"})
        self.assertEqual(response.status_code, 400)

    @patch("listings.ai_views.generate_description", return_value="Fake.")
    def test_only_book_details_are_sent_to_ai(self, mock_ai):
        self.client.force_authenticate(self.user)
        self.client.post(self.url, PAYLOAD)
        sent = set(mock_ai.call_args.kwargs.keys())
        self.assertEqual(
            sent,
            {"title", "author", "edition", "subject", "condition", "course_name"},
        )