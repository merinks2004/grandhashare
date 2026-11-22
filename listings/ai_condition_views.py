from django.conf import settings
from drf_spectacular.utils import extend_schema
from PIL import Image, UnidentifiedImageError
from rest_framework import serializers, status
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .ai import AIUnavailable
from .ai_condition import PRICE_PERCENT, estimate_condition, price_range
from .models import Listing

MAX_IMAGE_BYTES = 2 * 1024 * 1024
MIME_BY_FORMAT = {"JPEG": "image/jpeg", "PNG": "image/png", "WEBP": "image/webp"}
CONDITION_LABELS = dict(Listing.CONDITION_CHOICES)


class EstimateRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    author = serializers.CharField(max_length=150)
    original_price = serializers.DecimalField(
        max_digits=8, decimal_places=2, min_value=1, required=False
    )
    images = serializers.ListField(
        child=serializers.FileField(), min_length=1, max_length=4
    )

    def validate_images(self, files):
        checked = []
        for f in files:
            if f.size > MAX_IMAGE_BYTES:
                raise serializers.ValidationError("Each photo must be 2 MB or smaller.")
            try:
                f.seek(0)
                fmt = Image.open(f).format  # Pillow really reads the file
                f.seek(0)
                data = f.read()
            except (UnidentifiedImageError, OSError):
                raise serializers.ValidationError("Only real image files are allowed.")
            if fmt not in MIME_BY_FORMAT:
                raise serializers.ValidationError("Use JPEG, PNG or WebP photos.")
            checked.append((data, MIME_BY_FORMAT[fmt]))
        return checked


class ConditionEstimateView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "ai_vision"

    @extend_schema(request=EstimateRequestSerializer, responses={200: dict})
    def post(self, request):
        serializer = EstimateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data

        try:
            condition, issues = estimate_condition(d["images"], d["title"], d["author"])
        except AIUnavailable as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        result = {
            "suggested_condition": condition,
            "condition_label": CONDITION_LABELS[condition],
            "issues": issues,
            "price_range": None,
            "note": (
                "AI estimate from photos only. It cannot see inside the book. "
                "Please check and change it before posting."
            ),
        }
        if "original_price" in d:
            low, high = price_range(d["original_price"], condition)
            pct = PRICE_PERCENT[condition]
            result["price_range"] = {"low": low, "high": high}
            result["price_note"] = (
                f"A rule of thumb: {pct[0]}-{pct[1]}% of the original price. "
                "It is not market data."
            )
        return Response(result)