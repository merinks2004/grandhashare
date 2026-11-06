from django.urls import path

from . import views

urlpatterns = [
    path("books/<int:pk>/request/", views.request_book, name="request_book"),
    path("requests/received/", views.requests_received, name="requests_received"),
    path("requests/mine/", views.my_requests, name="my_requests"),
    path("requests/<int:pk>/respond/", views.respond_request, name="respond_request"),
]