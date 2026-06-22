from django.urls import path

from . import views

app_name = "requests"

urlpatterns = [
    path("donate/", views.donate_request, name="donate"),
    path("purchase/", views.purchase_request, name="purchase"),
    path("contact/", views.contact_message, name="contact"),
]