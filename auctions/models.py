from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models import Max

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

DEFAULT_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/6/65/No-Image-Placeholder.svg"

class User(AbstractUser):
    # Fields required by criteria[4], "Watchlist"
    watching = models.ManyToManyField("Listing", blank=True, related_name="watchers")



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

    def __str__(self):
        return f"Auction {self.title}"

    def final_image_url(self):
        if self.image_url == "":
            return DEFAULT_IMAGE_URL
        else:
            return self.image_url

    def num_bids(self):
        return self.bids.count()

    def high_bid(self):
        return self.bids.aggregate(Max("amount"))


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
