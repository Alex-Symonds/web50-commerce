from .consts import CHARS_TITLE_LISTS, CHARS_DESC_LISTS

def gbp(price):
    return "£" + f"{price:,}"

def process_for_listpage(listings):
    # Index and category use the same info, so process it here
    results = []
    for l in listings:
        result = {}
        result["id"] = l.id
        result["image_url"] = l.final_image_url()
        result["title"] = l.truncate_title(CHARS_TITLE_LISTS)
        result["description"] = l.truncate_desc(CHARS_DESC_LISTS)

        hb = l.high_bid()
        if hb:
            result["current_price"] = gbp(hb.amount)
        else:
            result["current_price"] = gbp(l.starting_bid)

        results.append(result)

    return results

