from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.cache import cache
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .forms import SignupForm
from .verification import is_email_verified, read_token, send_verification_email


def signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            send_verification_email(user)
            messages.info(
                request,
                "Welcome! We sent a verification link to your email. "
                "Please verify it to post books or send requests.",
            )
            return redirect("/")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})


def verify_email(request, token):
    User = get_user_model()
    try:
        data = read_token(token)
        # The email in the link must still be the account's email.
        user = User.objects.get(pk=data["uid"], email=data["email"])
        profile = user.profile
    except (signing.BadSignature, User.DoesNotExist, KeyError, TypeError, AttributeError):
        return render(request, "accounts/verify_result.html", {"ok": False}, status=400)

    if not profile.email_verified:
        profile.email_verified = True
        profile.save(update_fields=["email_verified"])
    return render(request, "accounts/verify_result.html", {"ok": True})


@login_required
@require_POST
def resend_verification(request):
    user = request.user
    if is_email_verified(user):
        messages.info(request, "Your email is already verified.")
    elif not user.email:
        messages.error(request, "Your account has no email address.")
    elif not cache.add(f"verify-resend-{user.pk}", 1, 60):
        messages.error(request, "Please wait a minute before asking for another link.")
    else:
        send_verification_email(user)
        messages.success(request, "Verification link sent. Check your inbox and spam folder.")
    return redirect("/")