from rest_framework.permissions import BasePermission

from .verification import is_email_verified


class VerifiedEmailForCreate(BasePermission):
    """Reading is open. Creating needs a verified email."""

    message = "Please verify your email address first."

    def has_permission(self, request, view):
        if getattr(view, "action", None) != "create":
            return True
        return is_email_verified(request.user)