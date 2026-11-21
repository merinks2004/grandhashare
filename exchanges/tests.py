from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from listings.models import Course, Listing, University

from .models import BookRequest


class RequestAPITests(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")  # seller
        self.bob = User.objects.create_user("bob", password="pass12345")      # buyer
        self.carol = User.objects.create_user("carol", password="pass12345")  # stranger
        uni = University.objects.create(name="Test University")
        course = Course.objects.create(name="B.Tech CSE", university=uni)
        self.listing = Listing.objects.create(
            seller=self.alice, course=course, semester=2, title="Test Book",
            author="Author", subject="Maths", condition="good",
            listing_type="sell", price=100,
        )

    def send_request(self, user):
        self.client.force_authenticate(user)
        return self.client.post(
            reverse("bookrequest-list"), {"listing": self.listing.pk, "message": "Hi"}
        )

    def test_cannot_request_own_book(self):
        response = self.send_request(self.alice)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_request_twice(self):
        self.assertEqual(self.send_request(self.bob).status_code, 201)
        self.assertEqual(self.send_request(self.bob).status_code, 400)

    def test_cannot_request_unavailable_book(self):
        self.listing.status = "reserved"
        self.listing.save()
        self.assertEqual(self.send_request(self.bob).status_code, 400)

    def test_buyer_cannot_accept_own_request(self):
        req_id = self.send_request(self.bob).data["id"]
        url = reverse("bookrequest-accept", args=[req_id])
        self.assertEqual(self.client.post(url).status_code, 404)

    def test_seller_accept_reserves_book(self):
        req_id = self.send_request(self.bob).data["id"]
        self.client.force_authenticate(self.alice)
        response = self.client.post(reverse("bookrequest-accept", args=[req_id]))
        self.assertEqual(response.status_code, 200)
        self.listing.refresh_from_db()
        self.assertEqual(self.listing.status, "reserved")

    def test_cannot_answer_twice(self):
        req_id = self.send_request(self.bob).data["id"]
        self.client.force_authenticate(self.alice)
        url = reverse("bookrequest-reject", args=[req_id])
        self.assertEqual(self.client.post(url).status_code, 200)
        self.assertEqual(self.client.post(url).status_code, 400)

    def test_contact_hidden_until_accepted(self):
        response = self.send_request(self.bob)
        self.assertIsNone(response.data["contact"])

    def test_contact_visible_only_to_buyer_and_seller_after_accept(self):
        req_id = self.send_request(self.bob).data["id"]
        self.client.force_authenticate(self.alice)
        self.client.post(reverse("bookrequest-accept", args=[req_id]))
        detail = reverse("bookrequest-detail", args=[req_id])

        self.assertIsNotNone(self.client.get(detail).data["contact"])  # seller
        self.client.force_authenticate(self.bob)
        self.assertIsNotNone(self.client.get(detail).data["contact"])  # buyer
        self.client.force_authenticate(self.carol)
        self.assertEqual(self.client.get(detail).status_code, 404)     # stranger

    def test_reopen_revokes_contact(self):
        req_id = self.send_request(self.bob).data["id"]
        self.client.force_authenticate(self.alice)
        self.client.post(reverse("bookrequest-accept", args=[req_id]))
        self.listing.status = "available"  # same effect as Reopen
        self.listing.save()
        self.client.force_authenticate(self.bob)
        data = self.client.get(reverse("bookrequest-detail", args=[req_id])).data
        self.assertIsNone(data["contact"])