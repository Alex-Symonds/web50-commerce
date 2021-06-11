from .consts import CHARS_TITLE_LISTS, CHARS_DESC_LISTS
from .models import Listing, User

def gbp(price):
    """
    Format a number as GBP currency.
    """
    return "£" + f"{price:,}"

def process_for_listpage(listings):
    """
    Get a list of dictionaries with the necessary fields for an index page.
        Listings must be a filtered list of all listings that should appear.
    """
    # Index and category use the same info, so process it here
    results = []
    for l in listings:
        result = {}
        result["id"] = l.id
        result["image_url"] = l.final_image_url()
        result["title"] = l.truncate_title(CHARS_TITLE_LISTS)
        result["description"] = l.truncate_desc(CHARS_DESC_LISTS)
        result["created_on"] = l.created_on

        hb = l.high_bid()
        if hb:
            result["current_price"] = gbp(hb.amount)
        else:
            result["current_price"] = gbp(l.starting_bid)

        results.append(result)

    return results

def toggle_watchlist(listing_id, user):
    """
    Toggle watchlist membership based on whether this listing_id is already in this user's watchlist.
    """
    l = Listing.objects.get(id=listing_id)
    my_watchlist = user.watching.all()

    if l in my_watchlist:
        user.watching.remove(l)
    else:
        user.watching.add(l)

    return  