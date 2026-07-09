from django.contrib import admin

from .models import ContactMessage, DonationRequest, PurchaseRequest


@admin.register(PurchaseRequest)
class PurchaseRequestAdmin(admin.ModelAdmin):
	list_display = ("book_title", "user", "status", "created_at")
	list_filter = ("status",)
	search_fields = ("book_title", "author", "user__username")


@admin.register(DonationRequest)
class DonationRequestAdmin(admin.ModelAdmin):
	list_display = ("title", "author", "user", "condition", "status", "created_at")
	list_filter = ("status",)
	search_fields = ("title", "author", "user__username")


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
	list_display = ("subject", "name", "email", "is_read", "created_at")
	list_filter = ("is_read",)
	search_fields = ("subject", "name", "email")
