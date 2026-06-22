from django.urls import path

from . import views

app_name = "borrowing"

urlpatterns = [
    path("borrow/<int:inventory_id>/", views.request_borrow, name="request_borrow"),
    path("waitlist/<int:inventory_id>/", views.join_waitlist, name="join_waitlist"),
]