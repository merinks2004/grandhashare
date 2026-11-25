from functools import partial

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from listings.models import Listing

from .emails import notify_new_request, notify_request_answered
from .models import BookRequest
from .serializers import BookRequestSerializer
from accounts.permissions import VerifiedEmailForCreate


class BookRequestViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = BookRequestSerializer
    permission_classes = [IsAuthenticated, VerifiedEmailForCreate]

    def get_queryset(self):
        user = self.request.user
        return (
            BookRequest.objects.filter(Q(requester=user) | Q(listing__seller=user))
            .select_related("listing__seller__profile", "requester__profile")
        )

    def perform_create(self, serializer):
        book_request = serializer.save(requester=self.request.user)
        transaction.on_commit(partial(notify_new_request, book_request))

    def _respond(self, request, pk, new_status):
        # Only the seller of the listing can reach this object (else 404).
        get_object_or_404(BookRequest, pk=pk, listing__seller=request.user)

        with transaction.atomic():
            book_request = BookRequest.objects.select_for_update().get(pk=pk)
            listing = Listing.objects.select_for_update().get(pk=book_request.listing_id)

            if book_request.status != "pending":
                return Response({"detail": "You have already answered this request."},
                                status=status.HTTP_400_BAD_REQUEST)

            if new_status == "accepted":
                if listing.status != "available":
                    return Response({"detail": "This book is already reserved or sold."},
                                    status=status.HTTP_400_BAD_REQUEST)
                listing.status = "reserved"
                listing.save()

            book_request.status = new_status
            book_request.save()
            transaction.on_commit(partial(notify_request_answered, book_request))

        book_request = self.get_queryset().get(pk=pk)
        return Response(self.get_serializer(book_request).data)

    @action(detail=True, methods=["post"])
    def accept(self, request, pk=None):
        return self._respond(request, pk, "accepted")

    @action(detail=True, methods=["post"])
    def reject(self, request, pk=None):
        return self._respond(request, pk, "rejected")