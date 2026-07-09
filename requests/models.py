from django.contrib.auth.models import User
from django.db import models, transaction
from django.utils import timezone


class PurchaseRequest(models.Model):
	STATUS_CHOICES = [
		("pending", "Pending"),
		("approved", "Approved"),
		("rejected", "Rejected"),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchase_requests")
	isbn = models.CharField(max_length=20, blank=True)
	book_title = models.CharField(max_length=255)
	author = models.CharField(max_length=255, blank=True)
	reason = models.TextField()
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
	created_at = models.DateTimeField(auto_now_add=True)
	reviewed_at = models.DateTimeField(null=True, blank=True)
	review_notes = models.TextField(blank=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"PurchaseRequest({self.book_title} by {self.user.username})"


class DonationRequest(models.Model):
	STATUS_CHOICES = [
		("pending", "Pending"),
		("approved", "Approved"),
		("rejected", "Rejected"),
	]

	user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="donation_requests")
	isbn = models.CharField(max_length=20, blank=True)
	title = models.CharField(max_length=255)
	author = models.CharField(max_length=255)
	condition = models.CharField(max_length=120)
	notes = models.TextField(blank=True)
	status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
	created_at = models.DateTimeField(auto_now_add=True)
	reviewed_at = models.DateTimeField(null=True, blank=True)
	review_notes = models.TextField(blank=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"DonationRequest({self.title} by {self.user.username})"

	def approve(self, library):
		from catalog.models import Book, BookInventory

		if not self.isbn:
			raise ValueError("Donation requests need an ISBN to auto-create catalogue entries.")

		with transaction.atomic():
			book, _ = Book.objects.get_or_create(
				isbn=self.isbn,
				defaults={"title": self.title, "author": self.author},
			)
			inventory, created = BookInventory.objects.get_or_create(
				book=book,
				library=library,
				defaults={"total_copies": 1, "available_copies": 1},
			)
			if not created:
				inventory.total_copies += 1
				inventory.available_copies += 1
				inventory.save()

			self.status = "approved"
			self.reviewed_at = timezone.now()
			self.save(update_fields=["status", "reviewed_at"])
			return inventory


class ContactMessage(models.Model):
	name = models.CharField(max_length=255)
	email = models.EmailField()
	subject = models.CharField(max_length=255)
	message = models.TextField()
	is_read = models.BooleanField(default=False)
	created_at = models.DateTimeField(auto_now_add=True)

	class Meta:
		ordering = ["-created_at"]

	def __str__(self):
		return f"ContactMessage({self.subject})"
