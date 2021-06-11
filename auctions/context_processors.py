from django.conf import settings
from .models import User


def watchlist_count(request):
    """
    Set watchlist counter on the nav bar for the current user.
    """
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        watchlist_count = user.watching.count()
    else:
        watchlist_count = None

    return {
        "WATCHLIST_COUNT": watchlist_count
    }



