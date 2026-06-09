from django.contrib import admin
from .models import LibraryAdmin, UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "age")
    search_fields = ("user__username", "user__email")


@admin.register(LibraryAdmin)
class LibraryAdminAdmin(admin.ModelAdmin):
    list_display = ("user", "library")
    search_fields = ("user__username", "library__name")