from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from listings.models import Course, Listing, University

from .models import Profile


class SignupForm(UserCreationForm):
    email = forms.EmailField()
    phone = forms.CharField(max_length=15)
    college = forms.CharField(max_length=150)
    university = forms.ModelChoiceField(queryset=University.objects.all())
    course = forms.ModelChoiceField(queryset=Course.objects.all())
    semester = forms.TypedChoiceField(
        choices=Listing.SEMESTER_CHOICES, coerce=int
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        Profile.objects.create(
            user=user,
            phone=self.cleaned_data["phone"],
            college=self.cleaned_data["college"],
            university=self.cleaned_data["university"],
            course=self.cleaned_data["course"],
            semester=self.cleaned_data["semester"],
        )
        return user