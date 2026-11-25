from functools import partial

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from listings.models import Listing

from .emails import notify_new_request, notify_request_answered
from .forms import ReportForm, RequestForm
from .models import BookRequest, Report
from accounts.decorators import email_verified_required


@login_required
@email_verified_required
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
            transaction.on_commit(partial(notify_new_request, book_request))
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
    # 404 unless the logged-in user is the seller of this listing
    get_object_or_404(BookRequest, pk=pk, listing__seller=request.user)
    action = request.POST.get("action")

    with transaction.atomic():
        book_request = BookRequest.objects.select_for_update().get(pk=pk)
        listing = Listing.objects.select_for_update().get(pk=book_request.listing_id)

        if book_request.status != "pending":
            messages.info(request, "You have already answered this request.")
        elif action == "accept":
            if listing.status != "available":
                messages.error(request, "This book is already reserved or sold.")
            else:
                book_request.status = "accepted"
                book_request.save()
                listing.status = "reserved"
                listing.save()
                transaction.on_commit(partial(notify_request_answered, book_request))
                messages.success(request, "Request accepted. The book is now reserved.")
        elif action == "reject":
            book_request.status = "rejected"
            book_request.save()
            transaction.on_commit(partial(notify_request_answered, book_request))
            messages.success(request, "Request rejected.")
        else:
            messages.error(request, "Invalid action.")

    return redirect("requests_received")


@login_required
def report_listing(request, pk):
    listing = get_object_or_404(Listing, pk=pk)

    if listing.seller == request.user:
        messages.error(request, "You can't report your own book.")
        return redirect("listing_detail", pk=pk)

    if Report.objects.filter(listing=listing, reported_by=request.user).exists():
        messages.info(request, "You have already reported this book.")
        return redirect("listing_detail", pk=pk)

    if request.method == "POST":
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.listing = listing
            report.reported_by = request.user
            report.save()
            messages.success(request, "Thank you. We will review this listing.")
            return redirect("listing_detail", pk=pk)
    else:
        form = ReportForm()

    return render(
        request, "exchanges/report_listing.html",
        {"form": form, "listing": listing},
    )