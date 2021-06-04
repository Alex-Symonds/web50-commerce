from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create", views.create_listing, name="create_listing"),
    path("listings/<int:listing_id>", views.listing, name="listing"),
    path("watchlist", views.watchlist, name="watchlist"),
    path("listings/<int:listing_id>/bid", views.bid, name="bid"),
    path("listings/<int:listing_id>/close", views.close, name="close"),
    path("listings/<int:listing_id>/comment", views.add_comment, name="comment")
]
