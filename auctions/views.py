from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from .models import User, Listing, Bid, Comment
from .forms import NewListingForm
from . import util

from django.forms import ModelForm

def index(request):
    current = Listing.objects.filter(closed_on__isnull=True)

    for l in current:
        l.image_url = util.get_image_url(l.image_url)

    return render(request, "auctions/index.html", {
        "active_auctions": current
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


@login_required
def create_listing(request):
    if request.method == "POST":
        user_form = NewListingForm(request.POST)
        if user_form.is_valid():
            clean_title = user_form.cleaned_data["title"]
            clean_desc = user_form.cleaned_data["description"]
            clean_start_bid = user_form.cleaned_data["starting_bid"]
            clean_img_url = user_form.cleaned_data["image_url"]
            clean_category = user_form.cleaned_data["category"]
            user = request.user

            new_listing = Listing(title=clean_title, description=clean_desc, starting_bid=clean_start_bid, image_url=clean_img_url, category=clean_category, owner=user)
            new_listing.save()

            return HttpResponseRedirect(reverse("index"))

    else:
        return render(request, "auctions/create_listing.html", {
            "form": NewListingForm
        })

def listing(request, listing_id):
    listing = Listing.objects.get(id=listing_id)
    listing.image_url = util.get_image_url(listing.image_url)

    user = User.objects.get(username=request.user)
    watching = listing in user.watching.all()

    return render(request, "auctions/listing.html", {
        "listing": listing,
        "watching": watching
    })

def watchlist(request):
    if request.method == "POST":
        listing_id = request.POST.get("listing_id", "")
        user = User.objects.get(username=request.user)
        l = Listing.objects.get(id=listing_id)

        if l in user.watching.all():
            user.watching.remove(l)
        else:
            user.watching.add(l)

        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))
    pass