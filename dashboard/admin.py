from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
	list_display = ("user", "title", "read_status", "created_at")
	list_filter = ("read_status",)
	search_fields = ("user__username", "title", "message")
