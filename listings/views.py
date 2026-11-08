from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.contrib.auth.models import User

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import ListingFilterForm, ListingForm
from .models import BookImage, Course, Listing, University
MAX_IMAGES = 4
MAX_IMAGE_SIZE = 2 * 1024 * 1024  # 2 MB


def home(request):
    available = Listing.objects.filter(status="available")
    latest = available.select_related("course__university", "seller").prefetch_related(
        "images"
    )[:8]
    universities = (
        University.objects.annotate(
            book_count=Count(
                "courses__listings", filter=Q(courses__listings__status="available")
            )
        )
        .filter(book_count__gt=0)
        .order_by("-book_count", "name")[:8]
    )
    stats = {
        "books": available.count(),
        "universities": University.objects.count(),
        "courses": Course.objects.count(),
        "students": User.objects.exclude(username__startswith="demo_").count(),
    }

    subjects = [
        {"label": "Mathematics", "icon": "bi-calculator"},
        {"label": "Programming", "icon": "bi-code-slash"},
        {"label": "Electronics", "icon": "bi-cpu"},
        {"label": "Accounting", "icon": "bi-cash-coin"},
        {"label": "Anatomy", "icon": "bi-heart-pulse"},
        {"label": "Law", "icon": "bi-bank"},
    ]

    return render(
        request, "listings/home.html",
        {"latest": latest, "universities": universities, "stats": stats, "subjects": subjects},
    )

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
        elif any(img.size > MAX_IMAGE_SIZE for img in images):
            image_error = "Each photo must be 2 MB or smaller."

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
    user_request = None
    if request.user.is_authenticated:
        user_request = listing.requests.filter(requester=request.user).first()
    return render(
        request, "listings/listing_detail.html",
        {"listing": listing, "images": images, "user_request": user_request},
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

@login_required
def my_listings(request):
    listings = (
        Listing.objects.filter(seller=request.user)
        .select_related("course__university")
        .prefetch_related("images")
    )
    return render(request, "listings/my_listings.html", {"listings": listings})


@login_required
def edit_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)
    if request.method == "POST":
        form = ListingForm(request.POST, instance=listing)
        if form.is_valid():
            form.save()
            messages.success(request, "Your listing has been updated.")
            return redirect("listing_detail", pk=listing.pk)
    else:
        form = ListingForm(instance=listing)
    return render(
        request, "listings/add_listing.html",
        {"form": form, "editing": True, "listing": listing},
    )


@login_required
def delete_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)
    if request.method == "POST":
        listing.delete()
        messages.success(request, "Your listing has been deleted.")
        return redirect("my_listings")
    return render(request, "listings/delete_listing.html", {"listing": listing})

@login_required
@require_POST
def complete_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)
    if listing.status != "reserved":
        messages.error(request, "Only a reserved book can be marked as completed.")
    else:
        listing.status = "sold"
        listing.save()
        messages.success(request, "Marked as completed. Well done!")
    return redirect("my_listings")


@login_required
@require_POST
def reopen_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk, seller=request.user)
    if listing.status != "reserved":
        messages.error(request, "Only a reserved book can be reopened.")
    else:
        listing.requests.filter(status="accepted").update(status="rejected")
        listing.status = "available"
        listing.save()
        messages.success(request, "The book is available again.")
    return redirect("my_listings")


def about(request):
    return render(request, "pages/about.html")


def contact(request):
    return render(request, "pages/contact.html")


def privacy(request):
    return render(request, "pages/privacy.html")


def terms(request):
    return render(request, "pages/terms.html")