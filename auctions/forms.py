from django.forms import ModelForm
from .models import Listing, Bid, Comment

class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'category', 'image_url', 'starting_bid', 'description']


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']