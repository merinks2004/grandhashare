from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from listings.models import Listing

from .forms import RequestForm
from .models import BookRequest
from django.views.decorators.http import require_POST


@login_required
def request_book(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if listing.seller == request.user:
        messages.error(request, "You can't request your own book.")
        return redirect("listing_detail", pk=pk)

    if listing.status != "available":
        messages.error(request, "This book is no longer available.")
        return redirect("listing_detail", pk=pk)

    if BookRequest.objects.filter(listing=listing, requester=request.user).exists():
        messages.info(request, "You have already requested this book.")
        return redirect("listing_detail", pk=pk)

    if request.method == "POST":
        form = RequestForm(request.POST)
        if form.is_valid():
            book_request = form.save(commit=False)
            book_request.listing = listing
            book_request.requester = request.user
            book_request.save()
            messages.success(request, "Request sent! The seller will review it.")
            return redirect("listing_detail", pk=pk)
    else:
        form = RequestForm()

    return render(
        request, "exchanges/request_book.html",
        {"form": form, "listing": listing},
    )

@login_required
def requests_received(request):
    received = BookRequest.objects.filter(
        listing__seller=request.user
    ).select_related("listing", "requester", "requester__profile")
    return render(request, "exchanges/requests_received.html", {"requests": received})


@login_required
def my_requests(request):
    sent = BookRequest.objects.filter(
        requester=request.user
    ).select_related("listing", "listing__seller", "listing__seller__profile")
    return render(request, "exchanges/my_requests.html", {"requests": sent})


@login_required
@require_POST
def respond_request(request, pk):
    book_request = get_object_or_404(
        BookRequest.objects.select_related("listing"),
        pk=pk,
        listing__seller=request.user,
    )
    action = request.POST.get("action")

    if book_request.status != "pending":
        messages.info(request, "You have already answered this request.")
    elif action == "accept":
        if book_request.listing.status != "available":
            messages.error(request, "This book is already reserved or sold.")
        else:
            book_request.status = "accepted"
            book_request.save()
            book_request.listing.status = "reserved"
            book_request.listing.save()
            messages.success(request, "Request accepted. The book is now reserved.")
    elif action == "reject":
        book_request.status = "rejected"
        book_request.save()
        messages.success(request, "Request rejected.")
    else:
        messages.error(request, "Invalid action.")

    return redirect("requests_received")

