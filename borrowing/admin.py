from django.contrib import admin

from .models import BorrowRecord, WaitlistEntry


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
	list_display = ("user", "book_inventory", "status", "request_date", "due_date")
	list_filter = ("status",)
	search_fields = ("user__username", "book_inventory__book__title", "book_inventory__library__name")


@admin.register(WaitlistEntry)
class WaitlistEntryAdmin(admin.ModelAdmin):
	list_display = ("user", "book_inventory", "timestamp", "notified")
	list_filter = ("notified",)
	search_fields = ("user__username", "book_inventory__book__title")
