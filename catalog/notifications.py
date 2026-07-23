"""
Notifications helper.

`notify(user, title, message)` does two things at once:
  1. creates an in-app Notification row (the bell on the dashboard), and
  2. emails the user the same message, if they have an email address.

Every place that used to call `Notification.objects.create(...)` should call this
instead, so users are told about approvals, rejections, and waitlist openings by
email as well as in the app. Email sending is best-effort: if the mail server is
unreachable the in-app notification is still saved.
"""
from django.conf import settings
from django.core.mail import send_mail


def notify(user, title, message):
    from .models import Notification

    notification = Notification.objects.create(user=user, title=title, message=message)

    if user.email:
        try:
            send_mail(
                subject=f"LibraryTrack — {title}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            # Never let an email problem break the request; the in-app
            # notification has already been saved.
            pass

    return notification
