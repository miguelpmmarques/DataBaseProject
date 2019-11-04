from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import CustomUser


class CustomUserForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "citizen_card",
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
            "phone",
            "image",
        )

        def clean(self):
            cleaned_data = super(CustomUserForm, self).clean()
            mail = cleaned_data.get("email")
            mail_exists = WhitelistedMail.objects.filter(email=mail).exists()
            mail_used = CustomUser.objects.filter(email=mail).exists()
            msg = None
            if not mail_exists:
                msg = "Mail Doesn't Exist"
            elif mail_used:
                msg = "Specified email already in use"
            if msg:
                raise forms.ValidationError(msg)
            return cleaned_data
