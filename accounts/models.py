from django.conf import settings
from django.db import models

from listings.models import Course, University


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )
    phone = models.CharField(max_length=15)
    college = models.CharField(max_length=150)
    university = models.ForeignKey(
        University, on_delete=models.SET_NULL, null=True, blank=True
    )
    course = models.ForeignKey(
        Course, on_delete=models.SET_NULL, null=True, blank=True
    )
    semester = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"