from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import ContactMessageForm, DonationRequestForm, PurchaseRequestForm


def donate_request(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")

    form = DonationRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        donation = form.save(commit=False)
        donation.user = request.user
        donation.save()
        messages.success(request, "Donation request submitted for review.")
        return redirect("dashboard:member")

    return render(request, "requests/donation_form.html", {"form": form})


def purchase_request(request):
    if not request.user.is_authenticated:
        return redirect("accounts:login")

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

