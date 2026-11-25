import re

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase
from django.urls import reverse

OLD = "OldPass12345!"
NEW = "BrandNewPass!2026x"


class PasswordResetTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alice", "alice@example.com", OLD)

    def test_reset_page_loads(self):
        self.assertEqual(self.client.get(reverse("password_reset")).status_code, 200)

    def test_known_email_gets_a_link(self):
        response = self.client.post(reverse("password_reset"), {"email": "alice@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, ["alice@example.com"])
        self.assertIn("/accounts/reset/", mail.outbox[0].body)

    def test_unknown_email_looks_the_same_and_sends_nothing(self):
        response = self.client.post(reverse("password_reset"), {"email": "nobody@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)

    def test_full_reset_flow(self):
        self.client.post(reverse("password_reset"), {"email": "alice@example.com"})
        link = re.search(r"http://testserver(/accounts/reset/\S+)", mail.outbox[0].body).group(1)

        # Django swaps the token for a session link, then shows the form.
        response = self.client.get(link, follow=True)
        self.assertEqual(response.status_code, 200)
        form_url = response.redirect_chain[-1][0]

        response = self.client.post(form_url, {"new_password1": NEW, "new_password2": NEW})
        self.assertRedirects(response, reverse("password_reset_complete"))

        self.assertTrue(self.client.login(username="alice", password=NEW))

    def test_old_password_stops_working(self):
        self.client.post(reverse("password_reset"), {"email": "alice@example.com"})
        link = re.search(r"http://testserver(/accounts/reset/\S+)", mail.outbox[0].body).group(1)
        response = self.client.get(link, follow=True)
        form_url = response.redirect_chain[-1][0]
        self.client.post(form_url, {"new_password1": NEW, "new_password2": NEW})
        self.assertFalse(self.client.login(username="alice", password=OLD))

    def test_link_cannot_be_reused(self):
        self.client.post(reverse("password_reset"), {"email": "alice@example.com"})
        link = re.search(r"http://testserver(/accounts/reset/\S+)", mail.outbox[0].body).group(1)
        response = self.client.get(link, follow=True)
        form_url = response.redirect_chain[-1][0]
        self.client.post(form_url, {"new_password1": NEW, "new_password2": NEW})

        fresh_client = self.client_class()
        reused = fresh_client.get(link, follow=True)
        self.assertContains(reused, "This link does not work")

    def test_garbage_link_is_rejected(self):
        response = self.client.get("/accounts/reset/abc/not-a-token/", follow=True)
        self.assertContains(response, "This link does not work")