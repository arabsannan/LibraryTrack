from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect

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
		messages.error(request, "You already have the maximum number of active loans.")
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
	WaitlistEntry.objects.get_or_create(user=request.user, book_inventory=inventory)
	messages.success(request, "You have been added to the waitlist.")
	return redirect("catalog:book_detail", isbn=inventory.book.isbn)
