from django.shortcuts import render

from .models import Listing


def home(request):
    latest = Listing.objects.filter(status="available").select_related(
        "course__university"
    )[:6]
    return render(request, "listings/home.html", {"latest": latest})