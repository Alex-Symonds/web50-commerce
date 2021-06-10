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
from .forms import NewListingForm, BidForm, CommentForm
from .util import gbp, process_for_listpage
from .consts import CHARS_TITLE_LISTS, CHARS_DESC_LISTS

from django.forms import ModelForm




def index(request):
    current = Listing.objects.filter(closed_on__isnull=True)

    return render(request, "auctions/index.html", {
        "active_auctions": process_for_listpage(current)
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
    """
    GET = Form to create a listing
    POST = Process the new listing and forward to index
    """
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
    """
    GET = Display a single listing
    """
    # Grab the listing and set the image URL to default if there isn't one
    myListing = Listing.objects.get(id=listing_id)
    myListing.image_url = myListing.final_image_url()

    # Prepare watchlist variables
    watching = False
    if request.user.is_authenticated:
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
    user_top_bid = None
    if request.user.is_authenticated:
        user_bids = user.bids_made.filter(listing=myListing)
        if user_bids.count() > 0:
            uhb = user_bids.order_by('-amount').first()
            user_top_bid = uhb.amount

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
        "comments": comments,
        "bid_form": BidForm,
        "comment_form": CommentForm
    })


@login_required
def watchlist(request):
    """
    POST = Toggle listing in watchlist
    GET = Display watchlist
    """
    CHARS_TITLE_WATCHLIST = 20
    # Prepare the user and current watchlist, which are needed either way
    user = User.objects.get(username=request.user)
    my_watchlist = user.watching.all()

    # Toggle listing in user's watchlist
    if request.method == "POST":
        listing_id = request.POST.get("listing_id", "")
        l = Listing.objects.get(id=listing_id)

        if l in my_watchlist:
            user.watching.remove(l)
        else:
            user.watching.add(l)

        return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))

    # Prepare watchlist info for template
    results = []
    for w in my_watchlist:
        r = {}

        # General stuff directly from the model
        r["id"] = w.id
        r["title"] = w.truncate_title(CHARS_TITLE_WATCHLIST)
        r["image_url"] = w.final_image_url()
        r["created_on"] = w.created_on
        r["closed_on"] = w.closed_on
        
        # Bid related fields
        b = w.high_bid()
        if b == None:
            r["high_bid"] = w.starting_bid
            r["is_active"] = w.closed_on == None
            r["leader"] = "no bids"            
        else:
            r["high_bid"] = b.amount
            r["is_active"] = not b.winning_bid
            r["leader"] = b.bidder.username
        

        # user-specific bid fields
        user_high_bid = "" 
        user_bids = user.bids_made.filter(listing=w)
        if user_bids.count() > 0:
            user_top_bid = user_bids.order_by('-amount').first()
            user_high_bid = str(user_top_bid.amount)
        r["user_high_bid"] = user_high_bid

        results.append(r)

    return render(request, "auctions/watchlist.html", {
        "watchlist": results
    })



@login_required
def bid(request, listing_id):
    """
    POST = Place a bid
    GET = Error page
    """
    error_message = "This page is supposed to go whooshing by when you place a bid. Try clicking the back arrow."

    if request.method == "POST":
        # Load as a form, create a bid object
        user_form = BidForm(request.POST)
        if user_form.is_valid():
            listing = Listing.objects.get(id=listing_id)
            bidder = User.objects.get(username=request.user)
            b = Bid(listing=listing, bidder=bidder, amount=user_form.cleaned_data["amount"])
        
            # Use the Bid class's "is_valid" method to validate the proposed bid.
            if b.is_valid():
                # Save the bid and send the user back to the listing page
                b.save()
                return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))
            else:
                # Prepare a helpful error message.
                error_message="Bid failed. Bid must be larger than the highest bid, £"
                hb = listing.high_bid()
                if hb:
                     error_message += str(hb.amount)
                else:
                    error_message += str(listing.starting_bid)
    
    # Error page
    return render(request, "auctions/error.html", {
        "error_message": error_message
    })



@login_required
def close(request, listing_id):
    """
    POST = Close a listing
    GET = Error page
    """
    error_message = "This page is supposed to go whooshing by when you close an auction. Try clicking the back arrow."

    if request.method == "POST":
        # Check the user owns the auction, in case there were client-side shenanigans
        listing = Listing.objects.get(id=listing_id)
        owner = listing.owner
        if request.user.username == owner.username:

            # Get the highest bid and declare it the winner
            hb = listing.high_bid()
            listing.closed_on = datetime.now()
            hb.winning_bid = True

            # Save changes
            listing.save()
            hb.save()

            # Render page
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))
        else:
            error_message = "You do not own this auction, so you can't close it."

    # Error page    
    return render(request, "auctions/error.html", {
        "error_message": error_message
    })



@login_required
def add_comment(request, listing_id):
    """
    POST = Add a comment to a listing
    GET = Error page
    """
    error_message = "This page is supposed to go whooshing by when you add a comment. Try clicking the back arrow."

    if request.method == "POST":
        listing = Listing.objects.get(id=listing_id)
        user = User.objects.get(username=request.user)
        user_form = CommentForm(request.POST)

        if user_form.is_valid():
            c = Comment(user=user, listing=listing, content=user_form.cleaned_data["content"])
            c.save()
            return HttpResponseRedirect(reverse("listing", kwargs={"listing_id":listing_id}))

    # Error page
    return render(request, "auctions/error.html", {
        "error_message": error_message
    })



def categories(request):
    """
    GET = Display a page showing a list of all categories, each of which links to a page filtering listings by that category.
    """
    # Prepare a list of category names and number of listings
    cats = []
    for cat in Listing.CATEGORIES:
        catDict = {}
        catDict["id"] = cat[0]
        catDict["name"] = cat[1]
        catDict["count"] = Listing.objects.filter(category=cat[0]).filter(closed_on__isnull=True).count()
        cats.append(catDict)
 
    # Sort the list by display name
    cats = sorted(cats, key=lambda cn: cn["name"])

    # Render the page
    return render(request, "auctions/categories.html", {
        "categories": cats
    })




def category(request, category_name):
    """
    GET = Display a page showing listings in a single category.
    """
    # Get the filtered listings
    listings = Listing.objects.filter(category=category_name).filter(closed_on__isnull=True)

    # Render the page
    return render(request, "auctions/index.html", {
        "heading": category_name,
        "active_auctions": process_for_listpage(listings)
    })  