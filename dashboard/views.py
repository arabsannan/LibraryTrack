from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView

from accounts.models import LibraryAdmin
from borrowing.models import BorrowRecord, WaitlistEntry
from catalog.models import Book, BookInventory, Notification

from requests.models import DonationRequest, PurchaseRequest

from .forms import AddBookForm, AdjustCopiesForm


def _require_admin_library(request):
    """Return the admin's library, or None if the user isn't a library admin."""
    admin = LibraryAdmin.objects.filter(user=request.user).select_related("library").first()
    return admin.library if admin else None


class MemberDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/member.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        active_loans = BorrowRecord.objects.filter(
            user=user,
            status__in=["pending", "approved", "overdue"],
        ).select_related("book_inventory__book", "book_inventory__library")
        # Keep overdue status current on view.
        for loan in active_loans:
            loan.refresh_overdue()

        context["active_loans"] = active_loans
        context["active_count"] = active_loans.count()
        context["overdue_count"] = active_loans.filter(status="overdue").count()
        context["loan_history"] = BorrowRecord.objects.filter(user=user).select_related(
            "book_inventory__book", "book_inventory__library",
        )[:5]
        context["waitlist"] = WaitlistEntry.objects.filter(user=user).select_related(
            "book_inventory__book", "book_inventory__library",
        )
        context["notifications"] = Notification.objects.filter(user=user)[:6]
        context["unread_count"] = Notification.objects.filter(user=user, read_status=False).count()
        # The member's own submissions, so they can track what they've offered.
        context["my_donations"] = DonationRequest.objects.filter(user=user)[:6]
        context["my_purchases"] = PurchaseRequest.objects.filter(user=user)[:6]
        recently_viewed = self.request.session.get("recently_viewed_books", [])
        context["recently_viewed_books"] = Book.objects.filter(isbn__in=recently_viewed)
        context["visit_count"] = self.request.session.get("visit_count", 0)
        return context


class AdminDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/admin.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()

        if not LibraryAdmin.objects.filter(user=request.user).exists():
            messages.error(request, "You do not have a library admin assignment.")
            return redirect("catalog:home")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        admin_profile = self.request.user.library_admin_profile
        library = admin_profile.library

        # Refresh overdue for this branch.
        for rec in BorrowRecord.objects.filter(book_inventory__library=library, status="approved"):
            rec.refresh_overdue()

        context["library"] = library
        context["inventory"] = library.inventories.select_related("book")
        context["inventory_count"] = library.inventories.count()
        context["pending_borrows"] = BorrowRecord.objects.filter(
            book_inventory__library=library, status="pending",
        ).select_related("user", "book_inventory__book")
        context["overdue_borrows"] = BorrowRecord.objects.filter(
            book_inventory__library=library, status="overdue",
        ).select_related("user", "book_inventory__book")
        context["donation_requests"] = DonationRequest.objects.filter(status="pending")[:10]
        context["purchase_requests"] = PurchaseRequest.objects.filter(status="pending")[:10]

        context["pending_count"] = context["pending_borrows"].count()
        context["overdue_count"] = context["overdue_borrows"].count()
        context["requests_count"] = (
            context["donation_requests"].count() + context["purchase_requests"].count()
        )
        return context


@login_required
def add_book(request):
    library = _require_admin_library(request)
    if library is None:
        messages.error(request, "You do not have a library admin assignment.")
        return redirect("catalog:home")

    form = AddBookForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save(library)
        messages.success(request, f'"{form.cleaned_data["title"]}" is now stocked at {library.name}.')
        return redirect("dashboard:admin")

    return render(request, "dashboard/add_book.html", {"form": form, "library": library})


@login_required
def adjust_copies(request):
    """Increase or decrease the copies of one title at the admin's library."""
    library = _require_admin_library(request)
    if library is None:
        messages.error(request, "You do not have a library admin assignment.")
        return redirect("catalog:home")

    if request.method == "POST":
        form = AdjustCopiesForm(request.POST)
        if form.is_valid():
            inventory = get_object_or_404(
                BookInventory, pk=form.cleaned_data["inventory_id"], library=library,
            )
            count = form.cleaned_data["copies"]
            noun = "copy" if count == 1 else "copies"

            if form.cleaned_data["action"] == "add":
                inventory.total_copies += count
                inventory.available_copies += count
                inventory.save()
                messages.success(
                    request,
                    f'Added {count} {noun} of "{inventory.book.title}". '
                    f"Now {inventory.available_copies}/{inventory.total_copies} available.",
                )
            else:
                # Only copies sitting on the shelf can be removed; the rest are
                # out on loan and have to come back first.
                if count > inventory.available_copies:
                    messages.error(
                        request,
                        f'Cannot remove {count} {noun} of "{inventory.book.title}" — only '
                        f"{inventory.available_copies} are on the shelf right now "
                        f"(the others are on loan).",
                    )
                else:
                    inventory.total_copies -= count
                    inventory.available_copies -= count
                    inventory.save()
                    messages.success(
                        request,
                        f'Removed {count} {noun} of "{inventory.book.title}". '
                        f"Now {inventory.available_copies}/{inventory.total_copies} available.",
                    )
        else:
            messages.error(request, "Please enter a valid number of copies.")
    return redirect("dashboard:admin")
