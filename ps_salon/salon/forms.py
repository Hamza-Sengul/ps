from django import forms
from .models import Product

class AddItemForm(forms.Form):
    product = forms.ModelChoiceField(queryset=Product.objects.all(), empty_label=None)