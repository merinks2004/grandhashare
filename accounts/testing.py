from .models import Profile


def make_verified(user):
    Profile.objects.update_or_create(
        user=user,
        defaults={"phone": "9876543210", "college": "Test College", "email_verified": True},
    )
    return user