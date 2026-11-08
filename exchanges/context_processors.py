from .models import BookRequest


def pending_requests(request):
    if request.user.is_authenticated:
        count = BookRequest.objects.filter(
            listing__seller=request.user, status="pending"
        ).count()
        return {"pending_requests_count": count}
    return {}