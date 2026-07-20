from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.generic import TemplateView

from accounts.models import LibraryAdmin
from catalog.notifications import notify

from .forms import ContactMessageForm, DonationRequestForm, PurchaseRequestForm
from .models import DonationRequest, PurchaseRequest


@login_required
def donate_request(request):
    form = DonationRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        donation = form.save(commit=False)
        donation.user = request.user
        donation.save()
        messages.success(request, "Donation request submitted for review.")
        return redirect("dashboard:member")
    return render(request, "requests/donation_form.html", {"form": form})


@login_required
def purchase_request(request):
    form = PurchaseRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        purchase = form.save(commit=False)
        purchase.user = request.user
        purchase.save()
        messages.success(request, "Purchase request submitted for review.")
        return redirect("dashboard:member")
    return render(request, "requests/purchase_form.html", {"form": form})


def contact_message(request):
    form = ContactMessageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Thanks for reaching out. We will reply soon.")
        return redirect("catalog:home")
    return render(request, "requests/contact_form.html", {"form": form})


def _admin_library(user):
    admin = LibraryAdmin.objects.filter(user=user).select_related("library").first()
    return admin.library if admin else None


@login_required
def approve_donation(request, pk):
    library = _admin_library(request.user)
    if library is None:
        messages.error(request, "You do not have a library admin assignment.")
        return redirect("catalog:home")

    donation = get_object_or_404(DonationRequest, pk=pk, status="pending")
    if request.method == "POST":
        donation.approve(library)
        notify(
            user=donation.user,
            title="Donation approved",
            message=f'Thank you! "{donation.title}" has been added to {library.name}. '
                    f"You can drop the book off at the branch desk at your convenience.",
        )
        messages.success(request, f'Added "{donation.title}" to {library.name}.')
    return redirect("dashboard:admin")


@login_required
def reject_donation(request, pk):
    library = _admin_library(request.user)
    if library is None:
        messages.error(request, "You do not have a library admin assignment.")
        return redirect("catalog:home")

    donation = get_object_or_404(DonationRequest, pk=pk, status="pending")
    if request.method == "POST":
        donation.status = "rejected"
        donation.reviewed_at = timezone.now()
        donation.save(update_fields=["status", "reviewed_at"])
        notify(
            user=donation.user,
            title="Donation not accepted",
            message=f'Your donation "{donation.title}" was not accepted at this time. '
                    f"This is usually because the branch already holds enough copies. "
                    f"Thank you for offering, and please consider donating other titles.",
        )
        messages.info(request, "Donation request rejected.")
    return redirect("dashboard:admin")


@login_required
def decide_purchase(request, pk, decision):
    library = _admin_library(request.user)
    if library is None:
        messages.error(request, "You do not have a library admin assignment.")
        return redirect("catalog:home")

    purchase = get_object_or_404(PurchaseRequest, pk=pk, status="pending")
    if request.method == "POST":
        approved = decision == "approve"
        purchase.status = "approved" if approved else "rejected"
        purchase.reviewed_at = timezone.now()
        purchase.save(update_fields=["status", "reviewed_at"])
        if approved:
            message = (
                f'Good news, your request for "{purchase.book_title}" was approved. '
                f"We'll order a copy and add it to the catalogue once it arrives; "
                f"watch your notifications for its listing."
            )
        else:
            message = (
                f'Your request for "{purchase.book_title}" was declined for now. '
                f"You're welcome to suggest it again later, or request a different title."
            )
        notify(
            user=purchase.user,
            title=f"Purchase request {'approved' if approved else 'declined'}",
            message=message,
        )
        messages.success(request, f"Purchase request {'approved' if approved else 'declined'}.")
    return redirect("dashboard:admin")


class AboutView(TemplateView):
    template_name = "requests/about.html"


class TeamView(TemplateView):
    template_name = "requests/team.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["members"] = [
            {"name": "Araba Affran-Annan", "role": "Accounts & User Management",
             "blurb": "Authentication, profiles, and session-based personalisation."},
            {"name": "Fady Philips", "role": "Book Catalogue & Search",
             "blurb": "Browsing, filtering, and the public-facing catalogue."},
            {"name": "Nikhil Girsa", "role": "Admin Dashboard & Inventory",
             "blurb": "The library control panel, stock, and notifications."},
            {"name": "Neftalem Gebremicael", "role": "Borrowing System",
             "blurb": "The full borrow lifecycle, returns, waitlists, and overdue rules."},
            {"name": "Utkarsh Kanade", "role": "Requests, Waitlist & Static Pages",
             "blurb": "Donations, purchase requests, and site information pages."},
        ]
        return context
