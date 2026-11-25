import logging

from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)


def _send(user, subject, body):
    if not user.email:
        return
    try:
        send_mail(
            " ".join(subject.split()),  # subjects must be one line
            body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            
        )
    except Exception:
        # An email problem must never break the request flow.
        logger.exception("Could not send email to user id %s", user.pk)


def _link(name, *args):
    return settings.SITE_URL + reverse(name, args=args)


def notify_new_request(book_request):
    listing = book_request.listing
    seller = listing.seller
    note = book_request.message.strip()[:300]
    body = (
        f"Hi {seller.username},\n\n"
        f"{book_request.requester.username} has requested your book "
        f"\"{listing.title}\".\n"
    )
    if note:
        body += f"\nTheir message: {note}\n"
    body += (
        f"\nLog in to accept or reject the request:\n"
        f"{_link('requests_received')}\n\n"
        "GrandhaShare"
    )
    _send(seller, f"New request for \"{listing.title}\"", body)


def notify_request_answered(book_request):
    listing = book_request.listing
    buyer = book_request.requester
    if book_request.status == "accepted":
        subject = f"Your request was accepted: \"{listing.title}\""
        body = (
            f"Hi {buyer.username},\n\n"
            f"Good news! The seller accepted your request for \"{listing.title}\".\n"
            "Log in to see the seller's contact details and arrange a meeting "
            "on campus:\n"
            f"{_link('listing_detail', listing.pk)}\n\n"
            "GrandhaShare"
        )
    else:
        subject = f"Update on your request: \"{listing.title}\""
        body = (
            f"Hi {buyer.username},\n\n"
            f"The seller could not accept your request for \"{listing.title}\" "
            "this time. You can browse other books here:\n"
            f"{settings.SITE_URL}/books/\n\n"
            "GrandhaShare"
        )
    _send(buyer, subject, body)