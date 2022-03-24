# Harvard's CS50w: Project 2, "Commerce", by Alex Symonds

## Introduction
A simple eBay-like auction site.  

## Specification and Provided Materials
Students were given:
* New Django project
* views, URLs and HTML templates for log in and log out already written
* view, URLs and HTML template for index had been started, but left as an empty "TODO" shell

Students were required to:
* Add models for auction listing, bids and comments
* Create listing (view, URL path, HTML)
* Active Listings (view, URL path, HTML)
* Individual Listing (view, URL path, HTML), with conditional content depending on: whether the user is logged in; the user's relationship with the auction (owner / bidder); the status of the auction
* Watchlist (view, URL path, HTML)
* Categories (view, URL path, HTML)
* Django admin interface setup so an admin can view, add, edit and delete any listing, comments and bids.

[Full specification here.](https://cs50.harvard.edu/web/2020/projects/2/commerce/)

## Beyond the Specification
* Added some extra features to the Watchlist:
    * Creating an auction automatically adds it to your Watchlist
    * Reports auction status
	* If you're the owner, it displays how much the auction value has increased from the starting price
	* If you're not the owner, it tells you how your bid is doing by displaying "top bid", "no bid" or "beaten #YourLastBidValue"
    * Added a counter to Watchlist's nav link, telling you how many items you have on your watchlist
* Made the Categories page display the number of listings in each category and apply different CSS (i.e. greyed out) if it's 0

## Pages
* index
* listing
* categories
* watchlist
* create_listing
* log in, register
* error

## Learning Comments
* Django database use/migrations and customisation of admin pages
* Working with a SQL database via Django models
* Bootstrap


