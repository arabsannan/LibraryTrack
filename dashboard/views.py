from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView

from accounts.models import LibraryAdmin
from borrowing.models import BorrowRecord
from catalog.models import Book
from .models import Notification


class MemberDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/member.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["active_loans"] = BorrowRecord.objects.filter(
            user=user,
            status__in=["pending", "approved", "overdue"],
        ).select_related("book_inventory__book", "book_inventory__library")
        context["loan_history"] = BorrowRecord.objects.filter(user=user).select_related(
            "book_inventory__book",
            "book_inventory__library",
        )[:10]
        context["notifications"] = Notification.objects.filter(user=user)[:5]
        recently_viewed = self.request.session.get("recently_viewed_books", [])
        context["recently_viewed_books"] = Book.objects.filter(isbn__in=recently_viewed)
        context["visit_count"] = self.request.session.get("visit_count", 0)
        return context


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/admin.html"

    def dispatch(self, request, *args, **kwargs):
        if not LibraryAdmin.objects.filter(user=request.user).exists():
            messages.error(request, "You do not have a library admin assignment.")
            return redirect("catalog:home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admin_profile = self.request.user.library_admin_profile
        library = admin_profile.library
        context["library"] = library
        context["inventory"] = library.inventories.select_related("book")
        context["pending_borrows"] = BorrowRecord.objects.filter(
            book_inventory__library=library,
            status="pending",
        ).select_related("user", "book_inventory__book")
        context["overdue_borrows"] = BorrowRecord.objects.filter(
            book_inventory__library=library,
            status="overdue",
        ).select_related("user", "book_inventory__book")
        return context
