from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .ai import AIUnavailable, generate_description
from .models import Listing


class DescriptionRequestSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=200)
    author = serializers.CharField(max_length=150)
    edition = serializers.CharField(max_length=50, required=False, allow_blank=True, default="")
    subject = serializers.CharField(max_length=150)
    condition = serializers.ChoiceField(choices=Listing.CONDITION_CHOICES)
    course_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")


class DescriptionSuggestView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "ai"

    @extend_schema(request=DescriptionRequestSerializer, responses={200: dict})
    def post(self, request):
        serializer = DescriptionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            text = generate_description(**serializer.validated_data)
        except AIUnavailable as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({
            "description": text,
            "note": "AI-generated suggestion. Please check and edit it before posting.",
        })