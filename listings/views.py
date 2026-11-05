from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ListingFilterForm, ListingForm
from .models import BookImage, Listing

MAX_IMAGES = 4


def home(request):
    latest = Listing.objects.filter(status="available").select_related(
        "course__university"
    )[:6]
    return render(request, "listings/home.html", {"latest": latest})


@login_required
def add_listing(request):
    image_error = None
    if request.method == "POST":
        form = ListingForm(request.POST)
        images = request.FILES.getlist("images")

        if len(images) > MAX_IMAGES:
            image_error = f"You can upload at most {MAX_IMAGES} photos."
        elif any(not img.content_type.startswith("image/") for img in images):
            image_error = "Only image files are allowed."

        if form.is_valid() and not image_error:
            listing = form.save(commit=False)
            listing.seller = request.user
            listing.save()
            for img in images:
                BookImage.objects.create(listing=listing, image=img)
            messages.success(request, "Your book has been posted!")
            return redirect("home")
    else:
        form = ListingForm()
    return render(
        request, "listings/add_listing.html",
        {"form": form, "image_error": image_error},
    )


def listing_detail(request, pk):
    listing = get_object_or_404(
        Listing.objects.select_related("course__university", "seller"),
        pk=pk,
    )
    images = listing.images.all()
    return render(
        request, "listings/listing_detail.html",
        {"listing": listing, "images": images},
    )


def listing_list(request):
    form = ListingFilterForm(request.GET)
    listings = (
        Listing.objects.filter(status="available")
        .select_related("course__university")
        .prefetch_related("images")
    )

    if form.is_valid():
        data = form.cleaned_data
        if data["q"]:
            listings = listings.filter(
                Q(title__icontains=data["q"])
                | Q(author__icontains=data["q"])
                | Q(subject__icontains=data["q"])
            )
        if data["university"]:
            listings = listings.filter(course__university=data["university"])
        if data["course"]:
            listings = listings.filter(course=data["course"])
        if data["semester"]:
            listings = listings.filter(semester=data["semester"])
        if data["condition"]:
            listings = listings.filter(condition=data["condition"])
        if data["listing_type"]:
            listings = listings.filter(listing_type=data["listing_type"])
        if data["min_price"] is not None:
            listings = listings.filter(price__gte=data["min_price"])
        if data["max_price"] is not None:
            listings = listings.filter(price__lte=data["max_price"])

    paginator = Paginator(listings, 9)
    page_obj = paginator.get_page(request.GET.get("page"))

    params = request.GET.copy()
    params.pop("page", None)

    return render(
        request, "listings/listing_list.html",
        {"form": form, "page_obj": page_obj, "querystring": params.urlencode()},
    )