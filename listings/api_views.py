import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Course, Listing, University
from .permissions import IsOwnerOrReadOnly
from .serializers import CourseSerializer, ListingSerializer, UniversitySerializer


class ListingFilter(django_filters.FilterSet):
    university = django_filters.NumberFilter(field_name="course__university")
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")

    class Meta:
        model = Listing
        fields = ["course", "semester", "condition", "listing_type", "status"]


class UniversityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.select_related("university")
    serializer_class = CourseSerializer
    filterset_fields = ["university"]


class ListingViewSet(viewsets.ModelViewSet):
    queryset = (
        Listing.objects.select_related("seller", "course__university")
        .prefetch_related("images")
    )
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ListingFilter
    search_fields = ["title", "author", "subject"]
    ordering_fields = ["date_posted", "price"]

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)