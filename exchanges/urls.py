from django.urls import path

from . import views

urlpatterns = [
    path("books/<int:pk>/request/", views.request_book, name="request_book"),
]