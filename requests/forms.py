from django import forms

from .models import ContactMessage, DonationRequest, PurchaseRequest


_TEXT = {"class": "form-control"}
_AREA = {"class": "form-control", "rows": 4}


class DonationRequestForm(forms.ModelForm):
    class Meta:
        model = DonationRequest
        fields = ["isbn", "title", "author", "condition", "notes"]
        widgets = {
            "isbn": forms.TextInput(attrs={**_TEXT, "placeholder": "e.g. 9780140449136"}),
            "title": forms.TextInput(attrs=_TEXT),
            "author": forms.TextInput(attrs=_TEXT),
            "condition": forms.TextInput(attrs={**_TEXT, "placeholder": "e.g. Like new, some wear"}),
            "notes": forms.Textarea(attrs=_AREA),
        }


class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = ["isbn", "book_title", "author", "reason"]
        widgets = {
            "isbn": forms.TextInput(attrs={**_TEXT, "placeholder": "Optional"}),
            "book_title": forms.TextInput(attrs=_TEXT),
            "author": forms.TextInput(attrs=_TEXT),
            "reason": forms.Textarea(attrs={**_AREA, "placeholder": "Why should we stock this?"}),
        }


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]
        widgets = {
            "name": forms.TextInput(attrs=_TEXT),
            "email": forms.EmailInput(attrs=_TEXT),
            "subject": forms.TextInput(attrs=_TEXT),
            "message": forms.Textarea(attrs=_AREA),
        }
