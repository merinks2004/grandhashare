from .verification import is_email_verified


def email_verification(request):
    user = getattr(request, "user", None)
    unverified = bool(user and user.is_authenticated and not is_email_verified(user))
    return {"email_unverified": unverified}