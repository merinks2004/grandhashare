from rest_framework.routers import DefaultRouter

from .api_views import CourseViewSet, ListingViewSet, UniversityViewSet

router = DefaultRouter()
router.register("universities", UniversityViewSet)
router.register("courses", CourseViewSet)
router.register("listings", ListingViewSet)

urlpatterns = router.urls