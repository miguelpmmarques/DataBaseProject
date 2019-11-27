from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm


from .models import CustomUser
from .models import Tournament
from .models import Team
from .models import Position
from .models import Goal


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

    """def clean(self):
        cleaned_data = super(CustomUserForm, self).clean()
        mail = cleaned_data.get("email")
        msg = None
        if not mail_exists:
            msg = "Mail Doesn't Exist"
        elif mail_used:
            msg = "Specified email already in use"
        if msg:
            raise forms.ValidationError(msg)
        return cleaned_data"""


class TeamCreationForm(ModelForm):
    class Meta:
        model = Team
        fields = ("name", "tournament", "teamLogo", "tactic")


class PositionsForm(ModelForm):
    class Meta:
        model = Position
        fields = ("name", "start")


class TournamentCreationForm(ModelForm):
    class Meta:
        model = Tournament
        fields = (
            "name",
            "beginTournament",
            "endTournament",
            "number_teams",
            "fields",
            "game_week_days",
            "days_without_games",
        )


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = ("scorer", "time")
