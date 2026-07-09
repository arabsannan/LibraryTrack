from django import forms

from .models import ContactMessage, DonationRequest, PurchaseRequest


class DonationRequestForm(forms.ModelForm):
    class Meta:
        model = DonationRequest
        fields = ["isbn", "title", "author", "condition", "notes"]


class PurchaseRequestForm(forms.ModelForm):
    class Meta:
        model = PurchaseRequest
        fields = ["isbn", "book_title", "author", "reason"]


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "subject", "message"]