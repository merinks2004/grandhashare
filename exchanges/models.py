from django.conf import settings
from django.db import models

from listings.models import Listing


class BookRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
    ]

    listing = models.ForeignKey(
        Listing, on_delete=models.CASCADE, related_name="requests"
    )
    requester = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_requests"
    )
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]
        constraints = [
            models.UniqueConstraint(
                fields=["listing", "requester"],
                name="one_request_per_user_per_listing",
            )
        ]

    def __str__(self):
        return f"{self.requester.username} -> {self.listing.title} ({self.status})"