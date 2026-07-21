from django.urls import path

from . import views

app_name = "requests"

urlpatterns = [
    path("donate/", views.donate_request, name="donate"),
    path("purchase/", views.purchase_request, name="purchase"),
    path("contact/", views.contact_message, name="contact"),
    path("about/", views.AboutView.as_view(), name="about"),
    path("team/", views.TeamView.as_view(), name="team"),
    path("donation/<int:pk>/approve/", views.approve_donation, name="approve_donation"),
    path("donation/<int:pk>/reject/", views.reject_donation, name="reject_donation"),
    path("purchase/<int:pk>/<str:decision>/", views.decide_purchase, name="decide_purchase"),
]
