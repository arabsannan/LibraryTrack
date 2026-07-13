from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm

from .models import UserProfile

class StyledPasswordResetForm(PasswordResetForm):
    """The 'enter your email' step, with our input styling."""
    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "you@example.com",
            "autocomplete": "email",
        }),
    )

class StyledSetPasswordForm(SetPasswordForm):
    """The 'choose a new password' step, with our input styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["new_password1"].widget.attrs.update({
            "class": "form-control", "autocomplete": "new-password",
        })
        self.fields["new_password2"].widget.attrs.update({
            "class": "form-control", "autocomplete": "new-password",
        })


class RegisterForm(forms.ModelForm):
    # Extra fields not on the User model
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)
    age = forms.IntegerField(min_value=1, required=False)
    profile_photo = forms.ImageField(required=False)

    class Meta:
        model = User
        fields = ["username", "email", "password"]
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password")
        p2 = cleaned_data.get("confirm_password")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class LoginForm(AuthenticationForm):
    # Reuses Django's built-in login form — handles username + password + error messages.
    pass


class EditProfileForm(forms.ModelForm):
    # Only age and photo are editable cause username and email are fixed after registration.
    class Meta:
        model = UserProfile
        fields = ["age", "profile_photo"]
