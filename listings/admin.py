from django.contrib import admin
from django.db.models import Count

from .models import BookImage, Course, Listing, University

admin.site.register(University)
admin.site.register(Course)
admin.site.register(BookImage)


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = (
        "title", "seller", "course", "listing_type", "status",
        "report_count", "date_posted",
    )
    list_filter = ("status", "listing_type", "condition")
    search_fields = ("title", "author", "seller__username")

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(num_reports=Count("reports"))

    @admin.display(description="Reports", ordering="num_reports")
    def report_count(self, obj):
        return obj.num_reports