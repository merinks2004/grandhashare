from django.contrib import admin

from .models import BookRequest, Report

admin.site.register(BookRequest)


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("listing", "reason", "reported_by", "date")
    list_filter = ("reason",)
    search_fields = ("listing__title", "reported_by__username")