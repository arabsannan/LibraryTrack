from django.contrib import admin

from .models import Book, BookInventory, Library, Notification


@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
	list_display = ("name", "address", "contact_information")
	search_fields = ("name", "address")


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
	list_display = ("title", "isbn", "author", "genre")
	search_fields = ("title", "isbn", "author", "genre")


@admin.register(BookInventory)
class BookInventoryAdmin(admin.ModelAdmin):
	list_display = ("book", "library", "total_copies", "available_copies")
	list_filter = ("library",)
	search_fields = ("book__title", "book__isbn", "library__name")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ("user", "title", "read_status", "created_at")
	list_filter = ("read_status",)
	search_fields = ("user__username", "title", "message")
