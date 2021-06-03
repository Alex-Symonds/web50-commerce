from .models import Listing, Bid

DEFAULT_IMAGE_URL = "https://upload.wikimedia.org/wikipedia/commons/6/65/No-Image-Placeholder.svg"

def get_top_bid(auction):
    pass

def get_image_url(img_url):
    if img_url == "":
        return DEFAULT_IMAGE_URL
    else:
        return img_url