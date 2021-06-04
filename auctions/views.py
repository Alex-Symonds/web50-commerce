from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.db.models import Max
import decimal
from datetime import datetime

from .models import User, Listing, Bid, Comment
from .forms import NewListingForm

from django.forms import ModelForm

def index(request):
    current = Listing.objects.filter(closed_on__isnull=True)

    for l in current:
        l.image_url = l.final_image_url()

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

    # Grab the listing and set the image URL to default if there isn't one
    myListing = Listing.objects.get(id=listing_id)
    myListing.image_url = myListing.final_image_url()

    # Prpeare watchlist variables
    user = User.objects.get(username=request.user)
    watching = myListing in user.watching.all()

    # Prepare listing-centric bid variables
    num_bids = myListing.num_bids()
    high_bid = None
    if num_bids == 0:
        current_price = myListing.starting_bid
    else:
        high_bid = myListing.high_bid()
        current_price = high_bid.amount

    # Prepare user-centric bid variables  
    #user_bids = Bid.objects.filter(bidder__username=user.username).filter(listing=myListing)
    user_bids = user.bids_made.filter(listing=myListing)
    user_top_bid = None
    if user_bids.count() > 0:
        user_top_bid = user_bids.order_by('-amount').first()

    # Prepare comments
    c = myListing.comments.all()
    if c:
        comments = c.order_by("-created_on")
    else:
        comments = c

    return render(request, "auctions/listing.html", {
        "listing": myListing,
        "watching": watching,
        "num_bids": num_bids,
        "current_price": current_price,
        "high_bid": high_bid,
        "user_top_bid": user_top_bid,
        "comments": comments
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



def bid(request, listing_id):
    error_message = "This page is supposed to go whooshing by when you place a bid. Try clicking the back arrow."

    if request.method == "POST":
        listing = Listing.objects.get(id=listing_id)
        bidder = User.objects.get(username=request.user)

        try:
            bid_value = decimal.Decimal(request.POST.get("new_bid", 0))

        except decimal.InvalidOperation:
            error_message = "Barter is not supported: all bids must be a number representing a monetary value."

        else:
            b = Bid(listing=listing, bidder=bidder, amount=bid_value)

            if b.is_valid():
                b.save()
                return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))
            else:
                hb = listing.high_bid()
                error_message="Bid failed. Bid must be larger than the highest bid, £" + str(hb.amount)
    
    return render(request, "auctions/error.html", {
        "error_message": error_message
    })

def close(request, listing_id):
    error_message = "This page is supposed to go whooshing by when you close an auction. Try clicking the back arrow."

    if request.method == "POST":
        listing = Listing.objects.get(id=listing_id)
        hb = listing.high_bid()

        listing.closed_on = datetime.now()
        hb.winning_bid = True

        listing.save()
        hb.save()
        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))
        
    return render(request, "auctions/error.html", {
        "error_message": error_message
    })


def add_comment(request, listing_id):
    error_message = "This page is supposed to go whooshing by when you add a comment. Try clicking the back arrow."

    if request.method == "POST":
        listing = Listing.objects.get(id=listing_id)
        user = User.objects.get(username=request.user)

        try:
            content = request.POST.get("new_comment", "")
        except:
            error_message = "Failed to add comment because Reasons."
        else:
            c = Comment(user=user, listing=listing, content=content)
            c.save()
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))

    return render(request, "auctions/error.html", {
        "error_message": error_message
    })