from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Course, Listing, University


def make_listing(seller, course, **extra):
    data = dict(
        seller=seller, course=course, semester=2, title="Test Book",
        author="Author", subject="Maths", condition="good",
        listing_type="sell", price=100,
    )
    data.update(extra)
    return Listing.objects.create(**data)


class ListingAPITests(APITestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pass12345")
        self.bob = User.objects.create_user("bob", password="pass12345")
        uni = University.objects.create(name="Test University")
        self.course = Course.objects.create(name="B.Tech CSE", university=uni)
        self.listing = make_listing(self.alice, self.course)

    def payload(self, **extra):
        data = {
            "course": self.course.pk, "semester": 2, "title": "New Book",
            "author": "Someone", "subject": "Physics", "condition": "good",
            "listing_type": "sell", "price": "150",
        }
        data.update(extra)
        return data

    def test_anyone_can_read_listings(self):
        response = self.client.get(reverse("listing-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_anonymous_cannot_create(self):
        response = self.client.post(reverse("listing-list"), self.payload())
        self.assertIn(response.status_code, (401, 403))

    def test_create_sets_seller_from_logged_in_user(self):
        self.client.force_authenticate(self.bob)
        response = self.client.post(
            reverse("listing-list"), self.payload(seller=self.alice.pk)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["seller_username"], "bob")

    def test_client_cannot_set_status(self):
        self.client.force_authenticate(self.bob)
        response = self.client.post(
            reverse("listing-list"), self.payload(status="sold")
        )
        self.assertEqual(response.data["status"], "available")

    def test_non_owner_cannot_edit_or_delete(self):
        self.client.force_authenticate(self.bob)
        url = reverse("listing-detail", args=[self.listing.pk])
        self.assertEqual(self.client.patch(url, {"title": "Hacked"}).status_code, 403)
        self.assertEqual(self.client.delete(url).status_code, 403)

    def test_owner_can_edit(self):
        self.client.force_authenticate(self.alice)
        url = reverse("listing-detail", args=[self.listing.pk])
        response = self.client.patch(url, {"title": "Updated"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_negative_price_rejected(self):
        self.client.force_authenticate(self.bob)
        response = self.client.post(reverse("listing-list"), self.payload(price="-5"))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_donate_forces_price_zero(self):
        self.client.force_authenticate(self.bob)
        response = self.client.post(
            reverse("listing-list"), self.payload(listing_type="donate", price="99")
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(float(response.data["price"]), 0.0)