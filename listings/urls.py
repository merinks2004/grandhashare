from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("books/add/", views.add_listing, name="add_listing"),
    path("books/<int:pk>/", views.listing_detail, name="listing_detail"),
    path("books/", views.listing_list, name="listing_list"),
]