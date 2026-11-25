import re
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser, User
from django.core import mail
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from listings.models import Course, Listing, University

from .models import Profile
from .testing import make_verified
from .verification import is_email_verified, make_token


def link_from(message):
    return re.search(r"(/accounts/verify/\S+)", message.body).group(1)


def make_unverified(username):
    user = User.objects.create_user(username, f"{username}@example.com", "pass12345")
    Profile.objects.create(user=user, phone="9876543210", college="Test College",
                           email_verified=False)
    return user


class SignupAndLinkTests(TestCase):
    def setUp(self):
        cache.clear()
        self.uni = University.objects.create(name="Test University")
        self.course = Course.objects.create(name="B.Tech CSE", university=self.uni)

    def signup(self):
        return self.client.post(reverse("signup"), {
            "username": "newbie", "email": "Newbie@Example.com",
            "phone": "9876543210", "college": "Test College",
            "university": self.uni.pk, "course": self.course.pk, "semester": 2,
            "password1": "StrongPass!2026x", "password2": "StrongPass!2026x",
        })

    def test_signup_sends_link_and_starts_unverified(self):
        self.assertEqual(self.signup().status_code, 302)
        user = User.objects.get(username="newbie")
        self.assertFalse(user.profile.email_verified)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["newbie@example.com"])
        self.assertIn("/accounts/verify/", mail.outbox[0].body)

    def test_link_verifies_and_can_be_clicked_twice(self):
        self.signup()
        link = link_from(mail.outbox[0])
        self.assertEqual(self.client.get(link).status_code, 200)
        self.assertTrue(User.objects.get(username="newbie").profile.email_verified)
        self.assertEqual(self.client.get(link).status_code, 200)

    def test_garbage_link_rejected(self):
        response = self.client.get(reverse("verify_email", args=["garbage"]))
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "This link does not work", status_code=400)

    def test_expired_link_rejected(self):
        self.signup()
        link = link_from(mail.outbox[0])
        with patch("accounts.verification.MAX_AGE", -1):
            self.assertEqual(self.client.get(link).status_code, 400)
        self.assertFalse(User.objects.get(username="newbie").profile.email_verified)

    def test_link_dies_if_email_changes(self):
        user = make_unverified("sam")
        token = make_token(user)
        user.email = "other@example.com"
        user.save()
        response = self.client.get(reverse("verify_email", args=[token]))
        self.assertEqual(response.status_code, 400)
        user.profile.refresh_from_db()
        self.assertFalse(user.profile.email_verified)


class HelperTests(TestCase):
    def test_anonymous_is_not_verified(self):
        self.assertFalse(is_email_verified(AnonymousUser()))

    def test_user_without_profile_is_not_verified(self):
        user = User.objects.create_user("noprofile", "n@example.com", "pass12345")
        self.assertFalse(is_email_verified(user))

    def test_unverified_and_verified_profiles(self):
        self.assertFalse(is_email_verified(make_unverified("sam")))
        user = User.objects.create_user("ok", "ok@example.com", "pass12345")
        self.assertTrue(is_email_verified(make_verified(user)))

    def test_superuser_is_trusted(self):
        admin = User.objects.create_superuser("boss", "b@example.com", "pass12345")
        self.assertTrue(is_email_verified(admin))


class APIGateTests(APITestCase):
    def setUp(self):
        cache.clear()
        self.alice = make_verified(User.objects.create_user("alice", password="pass12345"))
        self.bob = make_verified(User.objects.create_user("bob", password="pass12345"))
        self.newbie = make_unverified("newbie")
        uni = University.objects.create(name="Test University")
        self.course = Course.objects.create(name="B.Tech CSE", university=uni)
        self.listing = Listing.objects.create(
            seller=self.alice, course=self.course, semester=2, title="Test Book",
            author="Author", subject="Maths", condition="good",
            listing_type="sell", price=100,
        )

    def listing_payload(self):
        return {"course": self.course.pk, "semester": 2, "title": "New Book",
                "author": "Someone", "subject": "Physics", "condition": "good",
                "listing_type": "sell", "price": "150"}

    def test_unverified_can_still_read(self):
        self.client.force_authenticate(self.newbie)
        self.assertEqual(self.client.get(reverse("listing-list")).status_code, 200)

    def test_unverified_cannot_post_listing(self):
        self.client.force_authenticate(self.newbie)
        response = self.client.post(reverse("listing-list"), self.listing_payload())
        self.assertEqual(response.status_code, 403)

    def test_verified_can_post_listing(self):
        self.client.force_authenticate(self.bob)
        response = self.client.post(reverse("listing-list"), self.listing_payload())
        self.assertEqual(response.status_code, 201)

    def test_unverified_cannot_request_book(self):
        self.client.force_authenticate(self.newbie)
        response = self.client.post(reverse("bookrequest-list"), {"listing": self.listing.pk})
        self.assertEqual(response.status_code, 403)

    def test_verified_can_request_book(self):
        self.client.force_authenticate(self.bob)
        response = self.client.post(reverse("bookrequest-list"), {"listing": self.listing.pk})
        self.assertEqual(response.status_code, 201)


class ResendTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = make_unverified("sam")
        self.url = reverse("resend_verification")

    def test_resend_sends_one_email_then_waits(self):
        self.client.force_login(self.user)
        self.client.post(self.url)
        self.client.post(self.url)
        self.assertEqual(len(mail.outbox), 1)

    def test_verified_user_gets_no_email(self):
        make_verified(self.user)
        self.client.force_login(self.user)
        self.client.post(self.url)
        self.assertEqual(len(mail.outbox), 0)

    def test_login_required(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 0)

    def test_get_not_allowed(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(self.url).status_code, 405)