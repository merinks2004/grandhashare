from django import forms

from .models import BookRequest


class RequestForm(forms.ModelForm):
    class Meta:
        model = BookRequest
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(attrs={
                "rows": 3,
                "class": "form-control",
                "placeholder": "Hi! I study the same course. When can we meet on campus?",
            })
        }