from django.urls import path

from .views import BookDetailView, HomeView

app_name = "catalog"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("books/<slug:isbn>/", BookDetailView.as_view(), name="book_detail"),
]