from django.forms import ModelForm
from .models import Listing

class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'category', 'image_url', 'starting_bid', 'description']