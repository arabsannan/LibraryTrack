from datetime import timedelta

from django.contrib.auth.models import User
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone


class BorrowRecord(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("returned", "Returned"),
        ("overdue", "Overdue"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrow_records")
    book_inventory = models.ForeignKey("catalog.BookInventory", on_delete=models.CASCADE, related_name="borrow_records")
    request_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateTimeField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    return_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "book_inventory"],
                condition=Q(status__in=["pending", "approved", "overdue"]),
                name="unique_active_borrow_per_user_and_inventory",
            ),
        ]
        ordering = ["-request_date"]

    def __str__(self):
        return f"{self.user.username} - {self.book_inventory} ({self.status})"

    @property
    def is_active(self):
        return self.status in ("pending", "approved", "overdue")

    def refresh_overdue(self):
        """Flip an approved loan to overdue once its due date has passed."""
        if self.status == "approved" and self.due_date and self.due_date < timezone.now().date():
            self.status = "overdue"
            self.save(update_fields=["status"])
        return self.status

    def approve(self):
        from catalog.notifications import notify

        if self.status != "pending":
            return False

        inv = self.book_inventory
        if inv.available_copies < 1:
            return False

        self.status = "approved"
        self.approval_date = timezone.now()
        self.due_date = timezone.now().date() + timedelta(weeks=3)
        self.save()
        inv.available_copies -= 1
        inv.save()

        notify(
            user=self.user,
            title="Borrow request approved",
            message=f'"{inv.book.title}" is ready to collect from {inv.library.name}. '
                    f"Please return it by {self.due_date:%b %d, %Y}.",
        )
        return True

    def reject(self):
        from catalog.notifications import notify

        if self.status != "pending":
            return False
        self.status = "returned"
        self.return_date = timezone.now()
        self.save(update_fields=["status", "return_date"])
        notify(
            user=self.user,
            title="Borrow request declined",
            message=f'Your request for "{self.book_inventory.book.title}" was not approved. '
                    f"The book may already be on loan. You can join its waitlist from the "
                    f"catalogue to be notified when a copy frees up.",
        )
        return True

    def mark_returned(self):
        from catalog.notifications import notify

        if self.status not in ("approved", "overdue"):
            return False

        self.status = "returned"
        self.return_date = timezone.now()
        self.save()
        inv = self.book_inventory
        inv.available_copies += 1
        inv.save()

        # Notify the next person waiting, in queue order.
        with transaction.atomic():
            next_entry = (
                WaitlistEntry.objects.select_for_update()
                .filter(book_inventory=inv, notified=False)
                .order_by("timestamp")
                .first()
            )
            if next_entry:
                next_entry.notified = True
                next_entry.save(update_fields=["notified"])
                notify(
                    user=next_entry.user,
                    title="A book on your waitlist is available",
                    message=f'"{inv.book.title}" is back in stock at {inv.library.name}. '
                            f"You can borrow it now.",
                )
        return True


class WaitlistEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="waitlist_entries")
    book_inventory = models.ForeignKey(
        "catalog.BookInventory",
        on_delete=models.CASCADE,
        related_name="waitlist_entries",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "book_inventory"], name="unique_waitlist_entry"),
        ]
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.user.username} waitlisted {self.book_inventory}"
