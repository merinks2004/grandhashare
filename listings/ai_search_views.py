from urllib.parse import urlencode

from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .ai import AIUnavailable
from .ai_search import smart_search


class SmartSearchSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=200)


class SmartSearchView(APIView):
    permission_classes = [IsAuthenticated]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "ai_search"

    @extend_schema(request=SmartSearchSerializer, responses={200: dict})
    def post(self, request):
        serializer = SmartSearchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            filters, summary = smart_search(serializer.validated_data["query"])
        except AIUnavailable as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if not filters:
            return Response(
                {"detail": "I couldn't turn that into filters. Try something like: "
                           "data structures 3rd sem under 300"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        return Response({
            "filters": filters,
            "url": "/books/?" + urlencode(filters),
            "summary": summary,
        })