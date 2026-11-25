from django.contrib.auth.models import User
from django.test import TestCase

from listings.models import Course, Listing, University

from .models import Profile
from .testing import make_verified

ADD_URL = "/books/add/"


class AddBookGateTests(TestCase):
    def setUp(self):
        uni = University.objects.create(name="Test University")
        self.course = Course.objects.create(name="B.Tech CSE", university=uni)

        self.unverified = User.objects.create_user("newbie", "newbie@example.com", "pass12345")
        Profile.objects.create(user=self.unverified, phone="9876543210",
                               college="Test College", email_verified=False)
        self.verified = make_verified(
            User.objects.create_user("alice", "alice@example.com", "pass12345")
        )

    def payload(self):
        return {"course": self.course.pk, "semester": 2, "title": "Gate Test Book",
                "author": "Someone", "subject": "Physics", "condition": "good",
                "listing_type": "sell", "price": "150"}

    def test_anonymous_is_sent_to_login(self):
        response = self.client.get(ADD_URL)
        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)

    def test_unverified_page_is_blocked(self):
        self.client.force_login(self.unverified)
        response = self.client.get(ADD_URL)
        self.assertRedirects(response, "/", fetch_redirect_response=False)

    def test_unverified_post_creates_nothing(self):
        self.client.force_login(self.unverified)
        response = self.client.post(ADD_URL, self.payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Listing.objects.count(), 0)

    def test_verified_page_loads(self):
        self.client.force_login(self.verified)
        self.assertEqual(self.client.get(ADD_URL).status_code, 200)

    def test_verified_can_post(self):
        self.client.force_login(self.verified)
        response = self.client.post(ADD_URL, self.payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Listing.objects.count(), 1)