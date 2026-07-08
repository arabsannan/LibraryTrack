from django.urls import path

from . import views

app_name = "borrowing"

urlpatterns = [
    path("borrow/<int:inventory_id>/", views.request_borrow, name="request_borrow"),
    path("waitlist/<int:inventory_id>/", views.join_waitlist, name="join_waitlist"),
    path("approve/<int:record_id>/", views.approve_borrow, name="approve_borrow"),
    path("reject/<int:record_id>/", views.reject_borrow, name="reject_borrow"),
    path("return/<int:record_id>/", views.return_book, name="return_book"),
    path("history/", views.BorrowHistoryView.as_view(), name="history"),
]
