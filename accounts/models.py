from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator


class UserProfile(models.Model):
    # Extra info Django's default user account doesn't store.
    # Created automatically when a user registers.
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(13)],
        null=True,
        blank=True,
    )
    profile_photo = models.ImageField(
        upload_to="profile_photos/",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Profile({self.user.username})"


class LibraryAdmin(models.Model):
    # Marks a user as staff for one library branch.
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="library_admin_profile",
    )

    # FK to catalog.Library — lets Django resolve this after all apps have loaded.
    library = models.ForeignKey(
        "catalog.Library",
        on_delete=models.CASCADE,
        related_name="admins",
    )

    def __str__(self):
        return f"LibraryAdmin({self.user.username} → {self.library})"