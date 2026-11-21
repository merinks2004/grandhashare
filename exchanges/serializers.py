from rest_framework import serializers

from listings.models import Listing

from .models import BookRequest


class BookRequestSerializer(serializers.ModelSerializer):
    listing_code = serializers.SerializerMethodField()
    listing_title = serializers.CharField(source="listing.title", read_only=True)
    requester_username = serializers.CharField(source="requester.username", read_only=True)
    seller_username = serializers.CharField(source="listing.seller.username", read_only=True)
    contact = serializers.SerializerMethodField()

    class Meta:
        model = BookRequest
        fields = [
            "id", "listing", "listing_code", "listing_title", "message",
            "status", "date", "requester_username", "seller_username", "contact",
        ]
        read_only_fields = ["status", "date"]

    def get_listing_code(self, obj):
        return f"GS-{obj.listing_id:05d}"

    def get_contact(self, obj):
        """Other person's phone, only after acceptance, only to the two people involved."""
        request = self.context.get("request")
        if not request or obj.status != "accepted" or obj.listing.status == "available":
            return None
        if request.user == obj.requester:
            other = obj.listing.seller
        elif request.user == obj.listing.seller:
            other = obj.requester
        else:
            return None
        profile = getattr(other, "profile", None)
        return {"username": other.username, "phone": profile.phone if profile else None}

    def validate_listing(self, listing):
        user = self.context["request"].user
        if listing.seller == user:
            raise serializers.ValidationError("You can't request your own book.")
        if listing.status != "available":
            raise serializers.ValidationError("This book is no longer available.")
        if BookRequest.objects.filter(listing=listing, requester=user).exists():
            raise serializers.ValidationError("You have already requested this book.")
        return listing