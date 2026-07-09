from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import LoginForm, RegisterForm, EditProfileForm


class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        # If already logged in, prevent re-registration
        if request.user.is_authenticated:
            return redirect("catalog:home")
        return render(request, self.template_name, {"form": RegisterForm()})

    def post(self, request):
        form = RegisterForm(request.POST, request.FILES)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        # Create the User
        user = User.objects.create_user(
            username=form.cleaned_data["username"],
            email=form.cleaned_data["email"],
            password=form.cleaned_data["password"],
        )

        # Update UserProfile associated with user
        user.profile.age = form.cleaned_data.get("age")
        if form.cleaned_data.get("profile_photo"):
            user.profile.profile_photo = form.cleaned_data["profile_photo"]
        user.profile.save()

        login(request, user)
        messages.success(request, "Welcome to LibraryTrack!")
        return redirect("catalog:home")


class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("catalog:home")
        return render(request, self.template_name, {"form": LoginForm()})

    def post(self, request):
        form = LoginForm(request, data=request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        user = form.get_user()
        login(request, user)
        messages.success(request, f"Welcome back, {user.username}!")

        # Send user to the page they were trying to reach, or home
        return redirect(request.GET.get("next", "catalog:home"))


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, "You have been logged out.")
        return redirect("accounts:login")


class ProfileView(LoginRequiredMixin, View):
    template_name = "accounts/profile.html"
    
    def get(self, request):
        return render(request, self.template_name)


class EditProfileView(LoginRequiredMixin, View):
    template_name = "accounts/edit_profile.html"

    def get(self, request):
        form = EditProfileForm(instance=request.user.profile)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = EditProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form})

        form.save()
        messages.success(request, "Profile updated successfully.")
        return redirect("accounts:profile")