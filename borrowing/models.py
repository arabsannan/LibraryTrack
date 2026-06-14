from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


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
    status = models.CharField(
        max_length=10, choices=STATUS_CHOICES, default="pending"
    )

    class Meta:
        ordering = ["-request_date"]

    def __str__(self):
        return f"{self.user.username} – {self.book_inventory} ({self.status})"

    def approve(self):
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

        return True

    def mark_returned(self):
        if self.status not in ("approved", "overdue"):
            return False
        
        self.status = "returned"
        self.return_date = timezone.now()
        self.save()
        inv = self.book_inventory
        inv.available_copies += 1
        inv.save()
        
        return True