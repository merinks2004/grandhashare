from django.contrib import admin

# Register your models here.
from .models import University, Course

admin.site.register(University)
admin.site.register(Course)