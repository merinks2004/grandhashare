from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("books/add/", views.add_listing, name="add_listing"),
    path("books/<int:pk>/", views.listing_detail, name="listing_detail"),
    path("books/", views.listing_list, name="listing_list"),
    path("books/mine/", views.my_listings, name="my_listings"),
    path("books/<int:pk>/edit/", views.edit_listing, name="edit_listing"),
    path("books/<int:pk>/delete/", views.delete_listing, name="delete_listing"),
    path("books/<int:pk>/complete/", views.complete_listing, name="complete_listing"),
    path("books/<int:pk>/reopen/", views.reopen_listing, name="reopen_listing"),
]