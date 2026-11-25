from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from .verification import is_email_verified


def email_verified_required(view):
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not is_email_verified(request.user):
            messages.error(request, "Please verify your email first. We sent a link to your inbox.")
            return redirect("/")
        return view(request, *args, **kwargs)
    return wrapper