from django.core.validators import MinValueValidator
from django.db import models


class Library(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255, blank=True)
    contact_information = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
    

class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Book(models.Model):
    isbn = models.CharField(max_length=20, unique=True, db_index=True)
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    genres = models.ManyToManyField(Genre, blank=True, related_name="books")
    description = models.TextField(blank=True)
    age_rating = models.CharField(max_length=20, blank=True)
    cover_image = models.ImageField(upload_to="book_covers/", blank=True, null=True)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return f"{self.title} ({self.isbn})"
    


class BookInventory(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="inventories")
    library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name="inventories")
    total_copies = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)])
    available_copies = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["book", "library"], name="unique_book_per_library"),
        ]
        ordering = ["library__name", "book__title"]

    def __str__(self):
        return f"{self.book.title} at {self.library.name}"

    def save(self, *args, **kwargs):
        if self.available_copies > self.total_copies:
            self.available_copies = self.total_copies
        super().save(*args, **kwargs)