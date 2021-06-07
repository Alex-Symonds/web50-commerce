from django.conf import settings
from .models import User


def watchlist_count(request):

    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        watchlist_count = user.watching.count()
    else:
        watchlist_count = None

    return {
        "WATCHLIST_COUNT": watchlist_count
    }



