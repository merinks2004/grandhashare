from unittest.mock import patch

from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse
from rest_framework.test import APITestCase

from listings.models import Course, Listing, University


class EmailTests(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", "alice@example.com", "pass12345")
        self.bob = User.objects.create_user("bob", "bob@example.com", "pass12345")
        uni = University.objects.create(name="Test University")
        course = Course.objects.create(name="B.Tech CSE", university=uni)
        self.listing = Listing.objects.create(
            seller=self.alice, course=course, semester=2, title="Test Book",
            author="Author", subject="Maths", condition="good",
            listing_type="sell", price=100,
        )

    def send_request(self):
        self.client.force_authenticate(self.bob)
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(
                reverse("bookrequest-list"),
                {"listing": self.listing.pk, "message": "Is it available?"},
            )

    def answer(self, req_id, name):
        self.client.force_authenticate(self.alice)
        with self.captureOnCommitCallbacks(execute=True):
            return self.client.post(reverse(name, args=[req_id]))

    def test_new_request_emails_the_seller(self):
        self.send_request()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["alice@example.com"])
        self.assertIn("bob", mail.outbox[0].body)

    def test_accept_emails_the_buyer_without_contact_details(self):
        req_id = self.send_request().data["id"]
        mail.outbox.clear()
        self.answer(req_id, "bookrequest-accept")
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["bob@example.com"])
        self.assertIn("accepted", mail.outbox[0].subject)
        self.assertNotIn("phone", mail.outbox[0].body.lower())

    def test_reject_emails_the_buyer(self):
        req_id = self.send_request().data["id"]
        mail.outbox.clear()
        self.answer(req_id, "bookrequest-reject")
        self.assertEqual(mail.outbox[0].to, ["bob@example.com"])

    def test_failed_email_does_not_break_the_request(self):
        with patch("exchanges.emails.send_mail", side_effect=Exception("smtp down")):
            response = self.send_request()
        self.assertEqual(response.status_code, 201)