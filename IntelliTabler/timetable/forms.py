from django import forms
from .models import *
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

class RegistrationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email", )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = """
            <ul>
                <li id="charLength">Your password must contain at least 8 characters.</li>
                <li id="numCheck">Your password can’t be entirely numeric.</li>
            </ul>"""

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ("name",)


class FormatForm(forms.ModelForm):
    class Meta:
        model=Format
        fields = ("numPeriods","numWeeks",)


class TeacherForm(forms.ModelForm):
    class Meta:
        model=Teacher
        fields = ("name", "totalHours", "roomNum", "id")
        widgets = {
            "id": forms.HiddenInput(),
        }

class AvailabilityForm(forms.Form):
    checked = forms.BooleanField(required=False)
    period = forms.CharField()
    week = forms.IntegerField()



