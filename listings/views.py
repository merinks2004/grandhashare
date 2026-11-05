from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ListingForm
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