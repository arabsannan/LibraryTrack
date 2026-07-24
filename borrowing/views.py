from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView

from accounts.models import LibraryAdmin
from catalog.models import BookInventory

from .models import BorrowRecord, WaitlistEntry


@login_required
def request_borrow(request, inventory_id):
    inventory = get_object_or_404(BookInventory, pk=inventory_id)

    active_loans = BorrowRecord.objects.filter(
        user=request.user,
        status__in=["pending", "approved", "overdue"],
    ).count()
    if active_loans >= 10:
        messages.error(request, "You already have the maximum of 10 active loans.")
        return redirect("catalog:book_detail", isbn=inventory.book.isbn)

    if BorrowRecord.objects.filter(
        user=request.user,
        book_inventory=inventory,
        status__in=["pending", "approved", "overdue"],
    ).exists():
        messages.warning(request, "You already have an active request for this book.")
        return redirect("catalog:book_detail", isbn=inventory.book.isbn)

    BorrowRecord.objects.create(user=request.user, book_inventory=inventory)
    messages.success(request, "Your borrow request was submitted for approval.")
    return redirect("catalog:book_detail", isbn=inventory.book.isbn)


@login_required
def join_waitlist(request, inventory_id):
    inventory = get_object_or_404(BookInventory, pk=inventory_id)
    _, created = WaitlistEntry.objects.get_or_create(user=request.user, book_inventory=inventory)
    if created:
        messages.success(request, "You have joined the waitlist. We will notify you when a copy is free.")
    else:
        messages.info(request, "You are already on the waitlist for this book.")
    return redirect("catalog:book_detail", isbn=inventory.book.isbn)


def _user_manages(user, inventory):
    """True if the user is the library admin for this inventory's branch."""
    return LibraryAdmin.objects.filter(user=user, library=inventory.library).exists()


@login_required
def approve_borrow(request, record_id):
    record = get_object_or_404(BorrowRecord, pk=record_id)
    if not _user_manages(request.user, record.book_inventory):
        messages.error(request, "You can only manage loans for your own library.")
        return redirect("dashboard:admin")

    if request.method == "POST":
        if record.approve():
            messages.success(request, f"Approved {record.user.username}'s loan of \"{record.book_inventory.book.title}\".")
        else:
            messages.error(request, "That request could not be approved (no copies available or already handled).")
    return redirect("dashboard:admin")


@login_required
def reject_borrow(request, record_id):
    record = get_object_or_404(BorrowRecord, pk=record_id)
    if not _user_manages(request.user, record.book_inventory):
        messages.error(request, "You can only manage loans for your own library.")
        return redirect("dashboard:admin")

    if request.method == "POST":
        if record.reject():
            messages.info(request, "Borrow request declined.")
        else:
            messages.error(request, "That request could not be declined.")
    return redirect("dashboard:admin")


@login_required
def return_book(request, record_id):
    record = get_object_or_404(BorrowRecord, pk=record_id, user=request.user)
    if request.method == "POST":
        if record.mark_returned():
            messages.success(request, f"You returned \"{record.book_inventory.book.title}\". Thank you!")
        else:
            messages.error(request, "That loan is not currently active.")
    return redirect("borrowing:history")


class BorrowHistoryView(LoginRequiredMixin, ListView):
    template_name = "borrowing/history.html"
    context_object_name = "records"
    paginate_by = 15

    def get_queryset(self):
        qs = BorrowRecord.objects.filter(user=self.request.user).select_related(
            "book_inventory__book", "book_inventory__library"
        )
        for record in qs:
            record.refresh_overdue()
        return qs
