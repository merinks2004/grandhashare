from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import SimpleTestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from .ai import AIUnavailable
from .ai_search import clean_filters

UNIS = {1, 2}
COURSES = {10: 1, 20: 2}  # course id -> university id


class CleanFilterTests(SimpleTestCase):
    def clean(self, data):
        return clean_filters(data, UNIS, COURSES)

    def test_valid_values_kept(self):
        out = self.clean({"q": "data structures", "semester": 3, "condition": "good",
                          "listing_type": "sell", "max_price": 300.0})
        self.assertEqual(out["semester"], 3)
        self.assertEqual(out["max_price"], 300)

    def test_made_up_ids_dropped(self):
        out = self.clean({"university": 999, "course": 888})
        self.assertEqual(out, {})

    def test_bad_values_dropped(self):
        out = self.clean({"semester": 12, "condition": "great",
                          "listing_type": "steal", "max_price": -5})
        self.assertEqual(out, {})

    def test_course_sets_matching_university(self):
        out = self.clean({"course": 20, "university": 1})
        self.assertEqual(out["university"], 2)

    def test_booleans_are_not_numbers(self):
        self.assertEqual(self.clean({"semester": True, "max_price": True}), {})

    def test_long_keywords_trimmed(self):
        self.assertLessEqual(len(self.clean({"q": "x" * 500})["q"]), 60)

    def test_non_dict_rejected(self):
        with self.assertRaises(AIUnavailable):
            self.clean(["not", "a", "dict"])


class SmartSearchViewTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", password="pass12345")
        self.url = reverse("ai-search")

    def test_login_required(self):
        response = self.client.post(self.url, {"query": "maths"}, format="json")
        self.assertIn(response.status_code, (401, 403))

    @patch("listings.ai_search_views.smart_search",
           return_value=({"q": "data structures", "semester": 3}, "Showing: x"))
    def test_returns_safe_url(self, mock_ai):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, {"query": "data structures 3rd sem"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["url"], "/books/?q=data+structures&semester=3")

    @patch("listings.ai_search_views.smart_search", return_value=({}, ""))
    def test_no_filters_gives_422(self, mock_ai):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, {"query": "hello"}, format="json")
        self.assertEqual(response.status_code, 422)

    @patch("listings.ai_search_views.smart_search", side_effect=AIUnavailable("down"))
    def test_ai_down_gives_503(self, mock_ai):
        self.client.force_authenticate(self.user)
        response = self.client.post(self.url, {"query": "maths"}, format="json")
        self.assertEqual(response.status_code, 503)

    def test_empty_query_rejected(self):
        self.client.force_authenticate(self.user)
        self.assertEqual(self.client.post(self.url, {"query": ""}, format="json").status_code, 400)