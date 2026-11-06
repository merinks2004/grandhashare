from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from listings.models import Listing

from .forms import RequestForm
from .models import BookRequest


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