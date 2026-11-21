from django.urls import path
from rest_framework.routers import DefaultRouter

from .ai_views import DescriptionSuggestView
from .api_views import CourseViewSet, ListingViewSet, UniversityViewSet

router = DefaultRouter()
router.register("universities", UniversityViewSet)
router.register("courses", CourseViewSet)
router.register("listings", ListingViewSet)

urlpatterns = [
    path("ai/description/", DescriptionSuggestView.as_view(), name="ai-description"),
] + router.urls