from django import forms

from .models import Course, Listing, University

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

class ListingFilterForm(forms.Form):
    q = forms.CharField(
        required=False, label="Search",
        widget=forms.TextInput(attrs={"placeholder": "Title, author or subject"}),
    )
    university = forms.ModelChoiceField(
        queryset=University.objects.all(), required=False,
        empty_label="All universities",
    )
    course = forms.ModelChoiceField(
        queryset=Course.objects.select_related("university"), required=False,
        empty_label="All courses",
    )
    semester = forms.TypedChoiceField(
        choices=[("", "Any semester")] + Listing.SEMESTER_CHOICES,
        coerce=int, empty_value=None, required=False,
    )
    condition = forms.ChoiceField(
        choices=[("", "Any condition")] + Listing.CONDITION_CHOICES, required=False,
    )
    listing_type = forms.ChoiceField(
        choices=[("", "Any type")] + Listing.TYPE_CHOICES, required=False,
        label="Type",
    )
    min_price = forms.DecimalField(required=False, min_value=0, label="Min price")
    max_price = forms.DecimalField(required=False, min_value=0, label="Max price")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = "form-select"
            else:
                field.widget.attrs["class"] = "form-control"