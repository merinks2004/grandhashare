from django import forms

from .models import BookRequest, Report

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


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason", "details"]
        widgets = {
            "reason": forms.Select(attrs={"class": "form-select"}),
            "details": forms.Textarea(attrs={
                "rows": 3,
                "class": "form-control",
                "placeholder": "Tell us what is wrong (optional)",
            }),
        }