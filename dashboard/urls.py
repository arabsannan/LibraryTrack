from django.urls import path

from .views import AdminDashboardView, MemberDashboardView

app_name = "dashboard"

urlpatterns = [
    path("member/", MemberDashboardView.as_view(), name="member"),
    path("admin/", AdminDashboardView.as_view(), name="admin"),
]