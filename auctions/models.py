from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE

# Constants
MAX_BID_DIGITS = 13

# Constants for item categories
CAT_FASHION = "Fashion"
CAT_ELECTRONICS = "Electronics"
CAT_LEISURE = "Leisure"
CAT_HOME = "Home"
CAT_MOTOR = "Motors"
CAT_COLLECT = "Collectables"
CAT_BUSINESS = "Business"
CAT_HEALTH = "Health"
CAT_MEDIA = "Media"
CAT_MISC = "Other"



class User(AbstractUser):
    pass



class Listing(models.Model):
# Ebay top-level categories
    CATEGORIES = [
        (CAT_FASHION, "Fashion"),
        (CAT_ELECTRONICS, "Electronics"),
        (CAT_LEISURE, "Sports, Hobbies & Leisure"),
        (CAT_HOME, "Home & Garden"),
        (CAT_MOTOR, "Motors"),
        (CAT_COLLECT, "Collectables & Art"),
        (CAT_BUSINESS, "Business, Office & Industrial Supplies"),
        (CAT_HEALTH, "Health & Beauty"),
        (CAT_MEDIA, "Media"),
        (CAT_MISC, "Others")
    ]

    # Fields required by criteria[1], "Create Listing"
    title = models.CharField(max_length=140)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=MAX_BID_DIGITS, decimal_places=2)
    image_url = models.CharField(max_length=2000, blank=True)
    category = models.CharField(max_length=14, choices=CATEGORIES)

    # Fields required by criteria[2], "Active Listings Page"
    created_on = models.DateTimeField(auto_now_add=True)
    closed_on = models.DateTimeField(null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auctions")

    # Fields required by criteria[4], "Watchlist"
    watchers = models.ManyToManyField(User, blank=True, related_name="watching")

    def __str__(self):
        return f"Auction {self.title}"



class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids_made")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids")
    amount = models.DecimalField(max_digits=MAX_BID_DIGITS, decimal_places=2)
    created_on = models.DateTimeField(auto_now_add=True)
    winning_bid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.bidder} bid £{self.amount} on {self.listing.title}"



class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "comments_made")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} "
