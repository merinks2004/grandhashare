from django.db import models
from django.conf import settings

# Create your models here.
class University(models.Model):
    name = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name_plural = "universities"
        ordering = ["name"]

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=150)
    university = models.ForeignKey(
        University, on_delete=models.CASCADE, related_name="courses"
    )

    class Meta:
        ordering = ["university__name", "name"]

    def __str__(self):
        return f"{self.university.name} - {self.name}"
    
class Listing(models.Model):
    CONDITION_CHOICES = [
        ("like_new", "Like new"),
        ("good", "Good"),
        ("fair", "Fair"),
        ("poor", "Poor"),
    ]
    TYPE_CHOICES = [
        ("sell", "Sell"),
        ("swap", "Swap"),
        ("donate", "Donate"),
    ]
    STATUS_CHOICES = [
        ("available", "Available"),
        ("reserved", "Reserved"),
        ("sold", "Sold"),
    ]
    SEMESTER_CHOICES = [(i, f"Semester {i}") for i in range(1, 9)]

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="listings"
    )
    course = models.ForeignKey(
        Course, on_delete=models.CASCADE, related_name="listings"
    )
    semester = models.PositiveSmallIntegerField(choices=SEMESTER_CHOICES)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=150)
    edition = models.CharField(max_length=50, blank=True)
    subject = models.CharField(max_length=150)
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    listing_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="sell")
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="available")
    description = models.TextField(blank=True)
    date_posted = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_posted"]

    def __str__(self):
        return self.title