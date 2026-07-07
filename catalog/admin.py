from django.contrib import admin

from .models import Book, BookInventory, Genre, Library, Notification

@admin.register(Library)
class LibraryAdmin(admin.ModelAdmin):
	list_display = ("name", "address", "contact_information")
	search_fields = ("name", "address")

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ("title", "isbn", "author", "genre_list")
    search_fields = ("title", "isbn", "author", "genres__name")
    filter_horizontal = ("genres",)

    def genre_list(self, obj):
        return ", ".join(g.name for g in obj.genres.all())
    genre_list.short_description = "Genres"


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
