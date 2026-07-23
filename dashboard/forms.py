from django import forms

from catalog.models import Book, BookInventory, Genre


_TEXT = {"class": "form-control"}


class AddBookForm(forms.Form):
    """
    Add a book to the admin's library.

    If a book with the given ISBN already exists in the catalogue, we reuse it and
    just add (or top up) this library's inventory. Otherwise we create the book
    first. Either way the admin sets how many copies their library holds.
    """
    isbn = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={**_TEXT, "placeholder": "e.g. 9780140449136"}),
    )
    title = forms.CharField(
        max_length=255, widget=forms.TextInput(attrs=_TEXT),
    )
    author = forms.CharField(
        max_length=255, widget=forms.TextInput(attrs=_TEXT),
    )
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 6}),
        help_text="Hold Ctrl (or Cmd) to select more than one.",
    )
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={**_TEXT, "rows": 3}),
    )
    age_rating = forms.CharField(
        max_length=20, required=False,
        widget=forms.TextInput(attrs={**_TEXT, "placeholder": "e.g. All ages, Teen"}),
    )
    total_copies = forms.IntegerField(
        min_value=1, initial=1,
        widget=forms.NumberInput(attrs=_TEXT),
    )

    def save(self, library):
        data = self.cleaned_data
        book, created = Book.objects.get_or_create(
            isbn=data["isbn"],
            defaults={
                "title": data["title"],
                "author": data["author"],
                "description": data.get("description", ""),
                "age_rating": data.get("age_rating", ""),
            },
        )
        if data.get("genres"):
            book.genres.add(*data["genres"])

        copies = data["total_copies"]
        inventory, inv_created = BookInventory.objects.get_or_create(
            book=book,
            library=library,
            defaults={"total_copies": copies, "available_copies": copies},
        )
        if not inv_created:
            # Library already stocks this title — add the new copies on top.
            inventory.total_copies += copies
            inventory.available_copies += copies
            inventory.save()
        return inventory


class AdjustCopiesForm(forms.Form):
    """Increase or decrease the number of copies of one inventory row."""
    inventory_id = forms.IntegerField(widget=forms.HiddenInput)
    copies = forms.IntegerField(
        min_value=1, initial=1,
        widget=forms.NumberInput(attrs={"class": "form-control", "style": "width:80px;"}),
    )
    action = forms.ChoiceField(choices=[("add", "Add"), ("remove", "Remove")])
