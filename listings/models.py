from django.db import models

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