from django import forms

from .models import Listing


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            "course", "semester", "title", "author", "edition",
            "subject", "condition", "listing_type", "price", "description",
        ]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["price"].required = False
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned = super().clean()
        price = cleaned.get("price")
        if cleaned.get("listing_type") == "sell":
            if not price and "price" not in self.errors:
                self.add_error("price", "Enter a price for a book you want to sell.")
        else:
            cleaned["price"] = 0
        return cleaned