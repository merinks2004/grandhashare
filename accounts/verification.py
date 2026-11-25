import logging

from django.conf import settings
from django.core import signing
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)

SALT = "grandhashare-email-verify"
MAX_AGE = 24 * 60 * 60  # links work for 24 hours


def is_email_verified(user):
    """Fail closed: no profile means not verified. Superusers are trusted."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    profile = getattr(user, "profile", None)
    return bool(profile and profile.email_verified)


def make_token(user):
    # The email is inside the token, so changing the email breaks old links.
    return signing.dumps({"uid": user.pk, "email": user.email}, salt=SALT)


def read_token(token):
    """Returns the data, or raises signing.BadSignature (expired links too)."""
    return signing.loads(token, salt=SALT, max_age=MAX_AGE)


def send_verification_email(user):
    if not user.email:
        return False
    link = settings.SITE_URL + reverse("verify_email", args=[make_token(user)])
    body = (
        f"Hi {user.username},\n\n"
        "Welcome to GrandhaShare! Please confirm your email address by opening "
        "this link:\n\n"
        f"{link}\n\n"
        "The link works for 24 hours. If you did not create an account, "
        "you can ignore this email.\n\n"
        "GrandhaShare"
    )
    try:
        send_mail("Verify your GrandhaShare email", body, settings.DEFAULT_FROM_EMAIL, [user.email])
    except Exception:
        logger.exception("Could not send verification email to user id %s", user.pk)
        return False
    return True