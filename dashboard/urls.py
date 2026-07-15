from django.urls import path

from . import views
from .views import AdminDashboardView, MemberDashboardView

app_name = "dashboard"

urlpatterns = [
    path("member/", MemberDashboardView.as_view(), name="member"),
    path("admin/", AdminDashboardView.as_view(), name="admin"),
    path("admin/add-book/", views.add_book, name="add_book"),
    path("admin/adjust-copies/", views.adjust_copies, name="adjust_copies"),
]
