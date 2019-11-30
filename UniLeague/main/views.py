import json

from operator import itemgetter
import calendar
from datetime import datetime, date, timedelta, timezone
from random import choice, randint
from time import sleep
import math

from django import forms
from django.views.generic.dates import _date_from_string
from django.db.models.query import QuerySet
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.views.generic import View
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.urls import reverse_lazy
from django.urls import reverse
from django.views import generic
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.safestring import mark_safe
from django.utils import timezone
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.db.models import Count
from django.views.generic.dates import timezone_today

# third party imports

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import permissions

# internal imports

from .serializers import CustomUserSerializer
from .serializers import PartialCustomUserSerializer
from .serializers import GameWeekDaySerializer
from .serializers import TournamentSerializer
from .serializers import FieldSerializer
from .serializers import TeamSerializer
from .serializers import TeamSerializerCreate
from .serializers import PositionSerializer
from .serializers import TeamUserSerializer
from .serializers import GoalSerializer
from .serializers import TimeSlotSerializer

from .serializers import NotificationSerializer
from .serializers import ResultSerializer


from .tokens import account_activation_token
from .tasks import ask_admin_for_permissions
from .tasks import compareResults
from .forms import CustomUserForm
from .forms import TournamentCreationForm
from .forms import TeamCreationForm
from .forms import PositionsForm
from .forms import GoalForm


# from .forms import CustomUserLoginForm
from .models import CustomUser
from .models import GameWeekDay
from .models import Tournament
from .models import Day
from .models import Field
from .models import Team
from .models import TeamUser
from .models import Tactic
from .models import Notifications
from .models import RegularSlot
from .models import Position
from .models import Result
from .models import Game
from .models import TimeSlot
from .models import Goal

from .utils import Calendar

from django.views.generic.dates import YearArchiveView


TIME_SLOT_DURATION = timedelta(minutes=90)

# TINYURL.COM/SISTEMAS19


class NotificationsRestView(generics.RetrieveUpdateAPIView):
    queryset = Notifications.objects.all()
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]


class BaseCalendarView(YearArchiveView):
    model = TimeSlot
    date_field = "start_time"
    make_object_list = True
    template_name = "main/calendar.html"


class WeekCalendarView(generic.WeekArchiveView):
    model = TimeSlot
    date_field = "start_time"
    make_object_list = True
    allow_future = True
    week = timezone.now().isocalendar()[1]
    template_name = "main/calendar.html"

    def get_dated_items(self):
        """Return (date_list, items, extra_context) for this request."""
        year = timezone.now().year
        week = self.get_week()
        date_field = self.get_date_field()
        week_format = self.get_week_format()
        print("OLE==", week)
        week_choices = {"%W": "1", "%U": "0"}
        try:
            week_start = week_choices[week_format]
        except KeyError:
            raise ValueError(
                "Unknown week format %r. Choices are: %s"
                % (week_format, ", ".join(sorted(week_choices)))
            )
        date = _date_from_string(
            year, self.get_year_format(), week_start, "%w", week, week_format
        )
        since = self._make_date_lookup_arg(date)
        until = self._make_date_lookup_arg(self._get_next_week(date))
        lookup_kwargs = {"%s__gte" % date_field: since, "%s__lt" % date_field: until}
        qs = self.get_queryset()
        return (
            None,
            qs,
            {
                "week": date,
                "next_week": self.get_next_week(date),
                "previous_week": self.get_previous_week(date),
            },
        )

    def get_week(self):
        """Return the week for which this view should display data."""
        print("OIOI")
        week = self.week
        if week is None:
            try:
                week = self.kwargs["week"]
            except KeyError:
                try:
                    week = self.request.GET["week"]
                except KeyError:
                    raise Http404(_("No week specified"))
        return week

    def get_queryset(self):
        """
        Return the list of items for this view.
        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """
        print("HERE")
        pk = int(self.kwargs.get("pk"))
        games = Game.objects.filter(
            Q(home_team__pk=pk) | Q(away_team__pk=pk)
        ).values_list("pk")
        timeslots = (
            TimeSlot.objects.filter(game__pk__in=games)
            .filter(start_time__date__week=datetime.today().isocalendar()[1])
            .order_by("start_time")
        )
        print("TIMESLUTS===", timeslots)
        return timeslots

    def get(self, request, *args, **kwargs):
        print("OIOI")
        self.date_list, self.object_list, extra_context = self.get_dated_items()
        print("LLMLMLMLE")
        context = self.get_context_data(
            object_list=self.object_list, date_list=self.date_list, **extra_context
        )
        print(context)
        serializer = TimeSlotSerializer(context["timeslot_list"], many=True)

        return JsonResponse(serializer.data, safe=False)


# Create your views here.


class GoToTeamFromPlayer(generic.DetailView):
    template_name = "main/goToTeamFromPlayer.html"

    def get(self, request):

        teamuser = TeamUser.objects.all().order_by("player__first_name")
        return render(
            request, template_name=self.template_name, context={"users": teamuser}
        )


class TeamView(generic.DetailView):
    template_name = "main/profileTeam.html"

    def get(self, request, pk):
        print(request.user)
        if request.user.is_authenticated:

            teamuser = (
                TeamUser.objects.all()
                .filter(team__pk=pk)
                .filter(player__pk=request.user.id)
            ).first()

            print(teamuser)
            if teamuser == None:
                team_selected = Team.objects.filter(pk=pk).first()
                captainTeamUser = (
                    TeamUser.objects.filter(team__pk=pk).filter(isCaptain=True).first()
                )
            else:
                if teamuser.isCaptain:
                    print(request.user.teamuser_set.all)

                    team_selected = teamuser.team
                else:
                    try:
                        team_selected = Team.objects.filter(pk=pk).first()
                    except ValueError:
                        team_selected = None
        else:
            team_selected = Team.objects.get(pk=pk)
        if request.user.is_authenticated:
            thisUser = (
                TeamUser.objects.filter(team__pk=team_selected.pk)
                .filter(player=request.user.pk)
                .first()
            )
        else:
            thisUser = None

        try:
            context = {
                "captain": CustomUser.objects.filter(
                    pk__in=list(
                        TeamUser.objects.filter(team__pk=team_selected.pk)
                        .filter(isCaptain=True)
                        .values_list("player", flat=True)
                    )
                ).first(),
                "myTeam": team_selected,
                "thisUser": thisUser,
                "player_position": TeamUser.objects.filter(team__pk=team_selected.pk),
                "players": CustomUser.objects.filter(
                    pk__in=list(
                        TeamUser.objects.filter(team__pk=team_selected.pk).values_list(
                            "player", flat=True
                        )
                    )
                ),
                "tactic": team_selected.tactic,
                "positionsOcupied": TeamUser.objects.filter(
                    team__pk=team_selected.pk
                ).values_list("position", flat=True),
            }
            return render(request, template_name=self.template_name, context=context)
        except Exception as err:
            print("err===", err)
            raise Http404


class NotificationsView(generic.DetailView):
    template_name = "main/notifications.html"

    def get(self, request):
        if request.user.is_authenticated:
            notification = Notifications.objects.filter(
                user_send=request.user
            ).order_by("-sendDate")
            return render(
                request,
                template_name=self.template_name,
                context={"notifications": notification},
            )
        return HttpResponseRedirect(reverse("main:login-view"))


class ProfileView(generic.DetailView):
    template_name = "main/profile.html"
    model = CustomUser

    def get(self, request, pk):
        user = CustomUser.objects.get(pk=pk)
        return render(request, template_name=self.template_name, context={"user": user})


class CreateTeam(generic.CreateView):
    template_name = "main/createTeam.html"
    form_class = TeamCreationForm

    def get(self, request):

        tournaments = Tournament.objects.all()
        tactics = Tactic.objects.all()
        if request.user.is_authenticated:
            return render(
                request,
                template_name=self.template_name,
                context={
                    "form": self.form_class,
                    "tournaments": tournaments,
                    "tactics": tactics,
                },
            )
        return HttpResponseRedirect(reverse("main:landing-page"))

    def post(self, request):
        """
        overriding native post method, for e-mail sending with token verification
        """
        user = request.user

        if user.is_authenticated:
            form = TeamCreationForm(request.POST)
            already_has_team = True

            team_user_set = TeamUser.objects.filter(player__pk=user.pk)

            if form.is_valid():
                team = form.save(commit=False)

                for user in team_user_set:
                    if user.team.tournament.pk == team.tournament.pk:

                        messages.error(
                            request, "Já está inscrito numa equipa deste torneio"
                        )
                        return redirect("/teams/create/")

                request.session["team_form"] = TeamSerializer(team).data
                return redirect("/team/apply/0/")

            messages.error(request, form.errors)
            print(form.errors)
            return HttpResponseRedirect("")
        return HttpResponseRedirect(reverse("main:landing-page"))


class ChoosePositionView(generics.RetrieveUpdateAPIView):
    template_name = "main/teamApply.html"
    allowed_methods = "PATCH"
    serializer_class = PositionSerializer

    def get(self, request, pk):
        team_selected = Team.objects.filter(pk=pk).first()
        print(team_selected)
        if not team_selected:
            team_serialized = request.session["team_form"]
            tactic = Tactic.objects.get(pk=team_serialized["tactic"])
            return render(
                request,
                template_name=self.template_name,
                context={"team": team_serialized, "tactic": tactic},
            )
        else:
            return render(
                request,
                template_name=self.template_name,
                context={
                    "team": team_selected,
                    "tactic": team_selected.tactic,
                    "positionsOcupied": TeamUser.objects.filter(
                        team__pk=team_selected.pk
                    ).values_list("position", flat=True),
                },
            )

    def patch(self, request, pk):
        try:
            position = Position.objects.get(name=request.data["position"])
            print(position)
            team_exists = Team.objects.get(pk=pk)
            print(team_exists)
        except Position.DoesNotExist:
            raise Http404
        except Team.DoesNotExist:
            team_serialized = request.session["team_form"]
            team = TeamSerializerCreate(data=team_serialized)
            if team.is_valid(raise_exception=True):
                new_team = team.save()
                TeamUser.objects.create(
                    isCaptain=True,
                    player=request.user,
                    team=new_team,
                    position=position,
                ).save()
                print(request.user.first_name)
                print(request.user.last_name)
                print(new_team.name)
                print(new_team.tournament.name)
                print("GUARDOU")
                Notifications.objects.create(
                    title="OH CAPTAIN MY CAPTAIN",
                    description="<h3>"
                    + request.user.first_name
                    + " "
                    + request.user.last_name
                    + " you just became the captain of the team "
                    + new_team.name
                    + " in the tournament: "
                    + new_team.tournament.name
                    + " I wish you the best of luck in the matches!</h3> ",
                    user_send=request.user,
                    origin="Tournament Manager",
                ).save()
                return Response("success")
            else:
                print("\n\n" + team.errors)
        TeamUser.objects.create(
            isCaptain=False, player=request.user, team=team_exists, position=position
        ).save()
        Notifications.objects.create(
            title="WELCOME TO MY TEAM PARTER",
            description="<h3>"
            + request.user.first_name
            + " "
            + request.user.last_name
            + " you just joined the team "
            + team_exists.name
            + " in the tournament: "
            + team_exists.tournament.name
            + ". Please check out our team calendar and add capital to your "
            + "budget by sending money to this IBAN 0095 1666 1223 1233 2. We gonna win this!</h3>",
            user_send=request.user,
            origin="Captain",
        ).save()
        print(request.data["position"])

        return Response("success")


def profileOtherView(request, user_selected):
    user = CustomUser.objects.get(username=user_selected)
    return render(request, template_name="main/profile.html", context={"user": user})


def profileTeamOtherView(request, team_selected):
    print("Chegou aqui")
    team = Team.objects.get(name=team_selected)
    teamuser = TeamUser.objects.filter(team__name=team_selected)
    print(teamuser)
    return render(
        request,
        template_name="main/profileTeam.html",
        context={"myTeam": team, "teamuser": teamuser},
    )


class LandingPageView(generic.TemplateView):
    template_name = "main/MainMenu.html"

    def get(self, request):
        print("REQUEST===", self.request)
        if request.user.is_superuser:
            return HttpResponseRedirect("administration/")

        if request.user.is_authenticated:
            games = self.get_week_games(request.user)
        else:
            games = None
        try:
            tournaments = Tournament.objects.all()
            # .annotate(team_count=models.Count('article'))[0].article_count
            # teams = Team.objects.all().order_by(userteam_set__count)
            teams = (
                Team.objects.annotate(q_count=Count("teamuser"))
                .order_by("-q_count")
                .filter(q_count__lte=15)
            )
            teamCaptain = TeamUser.objects.filter(isCaptain=True)
            return render(
                request,
                template_name=self.template_name,
                context={
                    "teamCaptain": teamCaptain,
                    "teams": teams,
                    "tournaments": tournaments,
                    "games": games,
                },
            )

        except (Tournament.DoesNotExist, Team.DoesNotExist) as err:
            raise Http404

    def get_week_games(self, user):
        userTeam = TeamUser.objects.filter(player=user)
        games = Game.objects.none()
        next_week = datetime.today() + timedelta(days=7)
        for q in userTeam:
            home_games = Game.objects.filter(home_team=q.team).filter(
                gameDate__day__lte=next_week
            )
            away_games = Game.objects.filter(away_team=q.team).filter(
                gameDate__day__lte=next_week
            )

            temp = home_games | away_games
            games = games | temp
        games = games.distinct().order_by("-gameDate")
        return games


def log_out_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    print("Fez logout e chegou aqui")
    return HttpResponseRedirect(reverse("main:landing-page"))


class CreateTournamentListView(generic.TemplateView):
    template_name = "main/listTournament.html"

    def get(self, request):
        tournaments = Tournament.objects.all()
        return render(
            request,
            template_name=self.template_name,
            context={"tournaments": tournaments},
        )


class CreateTeamView(generic.TemplateView):
    template_name = "main/listTeam.html"

    def get(self, request):
        team = Team.objects.all()
        return render(
            request, template_name=self.template_name, context={"teams": team}
        )


# Create your views here.
class LoginView(generic.CreateView):
    template_name = "main/login.html"
    form_class = AuthenticationForm

    def get(self, request):
        if not request.user.is_authenticated:
            return render(
                request,
                template_name=self.template_name,
                context={"form": self.form_class},
            )
        return HttpResponseRedirect(reverse("main:landing-page"))

    def post(self, request):
        """
        Overriting the default post made by html form
        """
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(
                username=username, password=password
            )  # Gets Variables from HTML form
            login(
                request, user
            )  # Loggin already implemented by Django, lo sign in a user
            data = request.POST
            messages.error(request, "Logged in successfully")
            return HttpResponseRedirect(data.get("next", "/"))
        else:
            messages.error(
                request,
                "Login unsuccessful. Please enter the right password and username. Confirm your email if you haven't yet done so.",
            )
            return HttpResponseRedirect(reverse("main:login-view"))


class RegisterView(generic.CreateView):
    form_class = CustomUserForm
    template_name = "main/register.html"

    def post(self, request):
        """
        overriding native post method, for e-mail sending with token verification
        """
        form = CustomUserForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save(commit=False)
                    user.is_active = False
                    if user.pk == 1:
                        user.is_superuser = True
                    user.save()
            except IntegrityError as err:
                print("Database Integrity error:", err)
                return HttpResponse(
                    "Critical database error\nUnable to save your user\nPlease try again"
                )
            superuser = CustomUser.objects.get(is_superuser=True)
            Notifications.objects.create(
                title="NEW USER",
                description="<h3>The user "
                + user.username
                + " as know as "
                + user.first_name
                + " "
                + user.last_name
                + " has registered and would like to become a member of Unileague</h3><br><h3>",
                user_send=superuser,
                origin="System",
                html="</h3> <button name="
                + str(user.pk)
                + " class='btn btn-light btn-outline-secondary' id='activate_user'><span id='spinner' class='spinner-border spinner-border-sm' hidden='true'></span>ACTIVATE</button>",
            ).save()
            Notifications.objects.create(
                title="<h3>WELCOME TO UNILEAGUE",
                description="Welcome "
                + user.first_name
                + " "
                + user.last_name
                + " to the best soccer app in the world, join/create a team a start playing!</h3>",
                user_send=user,
                origin="System",
            ).save()
            current_site = get_current_site(request)
            mail_subject = "Activate your UniLeague account."
            message = render_to_string(
                "main/account_activation_email.html",
                {
                    "user": user,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                    "token": account_activation_token.make_token(user),
                },
            )
            to_email = form.cleaned_data.get("email")
            email = EmailMessage(mail_subject, message, to=[to_email])
            email.send()
            messages.error(request, "Confirm your account in your mail")
            return HttpResponseRedirect(reverse("main:landing-page"))
            for error in form.errors:
                print("error===", error)
        messages.error(request, form.errors)
        return HttpResponseRedirect(reverse("main:register"))


class HelpView(generic.TemplateView):
    template_name = "main/help.html"


class CreateTournamentView(APIView):
    # form_class = TournamentCreationForm
    """
    future optimization: mix a django form with the context, copy the request.data,
    pop the extra values and the send the copy to the forms
    """
    template_name = "main/create_tournament.html"
    allowed_methods = ("GET", "POST")
    game_week_day_serializer = GameWeekDaySerializer(
        GameWeekDay.objects.all(), many=True
    )
    list_to_send = []
    list_to_send_fields = []
    fields_serializer = FieldSerializer(Field.objects.all(), many=True)
    labels = {
        "name": {"value": "Tournament Name", "type": "text"},
        "number_teams": {"value": "Number of Teams", "type": "number"},
        "number_of_hands": {"value": "Number of Hands", "type": "number"},
        "beginTournament": {"value": "Begining of Tournament", "type": "date"},
        "endTournament": {"value": "End of Tournament", "type": "date"},
        "fields": {
            "value": "Game Fields",
            "type": "select",
            "choices": list_to_send_fields,
        },
        "tournament_badge": {"value": "Tournament Badge", "type": "file"},
        "game_week_days": {
            "value": "Game Week Days",
            "type": "checkbox",
            "choices": list_to_send,
        },
        "days_without_games": {"value": "Days Without Games", "type": "date"},
    }
    # success_url = reverse_lazy("login")
    def get(self, request):

        if request.user.is_authenticated:
            # send the week days list to present the checkbox
            for elem in self.game_week_day_serializer.data:
                if elem["week_day"] not in self.list_to_send:
                    self.list_to_send.append(elem["week_day"])
            # check if the list is in the correct order
            if not self.list_to_send[0] == "Monday":
                self.list_to_send.reverse()
            # change this to work in the same way as the fields to make it fully restfull
            self.labels["game_week_days"].update({"choices": self.list_to_send})
            # send the fields list
            for elem in self.fields_serializer.data:
                aux_elem = {"id": elem["id"], "name": elem["name"]}
                if aux_elem not in self.list_to_send_fields:
                    self.list_to_send_fields.append(aux_elem)
            self.labels["fields"].update({"choices": self.list_to_send_fields})
            # handmade form
            return render(
                request,
                template_name=self.template_name,
                context={"labels": self.labels},
            )
        else:
            return HttpResponseRedirect(reverse("main:landing-page"))

    def post(self, request):
        if request.user.is_authenticated:
            data = request.data
            # getting a mutable copy of the request data to modify and send to the serializer
            data_copy = data.copy()
            # ---------------------------------------------------
            # unnecessary once it's fully restfull, but for now, it's premature optimization
            for k in data.keys():
                if k in self.list_to_send:
                    data_copy.pop(k)
                    key = str(self.list_to_send.index(k))
                    dates = data_copy.get("game_week_days")
                    try:
                        fk = GameWeekDay.objects.get(week_day=key).pk
                        data_copy.update({"game_week_days": fk})
                    except GameWeekDay.DoesNotExist as err:
                        raise err
                # ------------------------------------------------
                if k == "days_without_games":
                    dates = data_copy.pop(k)
                    if dates[0] != "":
                        for elem in dates[0].split(","):
                            try:
                                day = Day.objects.get(day=elem)
                            except Day.DoesNotExist:
                                day = Day.objects.create(day=elem)
                            data_copy.update({k: day.pk})
                if k == "beginTournament" or k == "endTournament":
                    date = data.get(k)
                    data_copy.pop(k)
                    date = date + "T00:00"
                    data_copy.update({k: date})
            data_copy.update({"tournament_manager": request.user.pk})
            data_copy.update({"fields": 1})
            serializer = TournamentSerializer(data=data_copy)
            if serializer.is_valid():
                t = serializer.save()
                if self.generateTimeSlots(t):
                    request.user.isTournamentManager = True
                    request.user.save()
                    return Response({"sucess": True})
                else:
                    t.delete()
                    messages.error(
                        request,
                        "The timeframe you've provided for the tournament is to small for the amount of games that have to be generated. Try creating a game with less teams. There'll still be plenty of games to play!",
                    )
                    return HttpResponseRedirect("")
            print(serializer.errors)
            return Response({"errors": serializer.errors})
        else:
            return HttpResponseRedirect(reverse("main:landing-page"))

    def generateTimeSlots(self, tournament):
        number_of_teams = tournament.number_teams
        number_of_hands = tournament.number_of_hands
        num_games = nCr(number_of_teams, 2) * number_of_hands
        fields = tournament.fields.all()
        number_of_days = tournament.endTournament - tournament.beginTournament
        # tournament_aux = datetime.today().replace(tzinfo=pytz.UTC)
        # if tournament.beginTournament < tournament_aux:
        print("NOW===", timezone.now())
        print("beginTournament===", tournament.beginTournament)
        if tournament.beginTournament < timezone.now():
            day = timezone.now()
        else:
            day = tournament.beginTournament

        # going through all the days in the interval specified for the tournament to take place in
        for i in range(number_of_days.days):
            # checking if this day is was not forbidden by the tournament creator to have any games
            if tournament.days_without_games.filter(day=day).count() == 0:
                # checking if this day is a game week day
                if (
                    tournament.game_week_days.filter(week_day=day.weekday()).count()
                    != 0
                ):
                    # going through all the fields chosen by the administrator
                    for field in tournament.fields.all():
                        # getting the filed's timetable
                        timetable = RegularSlot.objects.filter(
                            week_day=day.weekday()
                        ).first()
                        if timetable:
                            slots = timetable.slots
                            for i in range(len(slots) - 1):
                                hour = slots[i].hour
                                minute = slots[i].minute
                                second = slots[i].second
                                aux_day = day.replace(
                                    hour=hour, minute=minute, second=second
                                )
                                try:
                                    TimeSlot.objects.create(
                                        title="",
                                        description="",
                                        start_time=aux_day,
                                        end_time=aux_day + TIME_SLOT_DURATION,
                                        cost="0",
                                        isFree=True,
                                        field=field,
                                        tournament=tournament,
                                    )
                                except IntegrityError:
                                    pass

            day = day + timedelta(days=1)
        number_of_timeslots = TimeSlot.objects.filter(
            tournament__pk=tournament.pk
        ).count()
        print("NUMBER OF TIMESLOTS===", number_of_timeslots)
        print("NUMBER OF GAMES TO PLAY===", num_games)

        if number_of_timeslots >= num_games:
            return True
        return False


class CreateGames(generic.CreateView):
    def get(self, request, tournament_pk):
        try:
            tournament = Tournament.objects.get(pk=tournament_pk)
            return render(request, "main/createGames.html", {"tournament": tournament})
        except Tournament.DoesNotExist:
            raise Http404

    def post(self, request, tournament_pk):
        try:
            tournament = Tournament.objects.get(pk=tournament_pk)
            number_of_teams = tournament.number_teams
            number_of_hands = tournament.number_of_hands
            num_games = nCr(number_of_teams, 2) * number_of_hands
            number_of_timeslots = TimeSlot.objects.filter(
                tournament__pk=tournament.pk
            ).count()
            print("NUMBER OF TIMESLOTS===", number_of_timeslots)
            print("NUMBER OF GAMES TO PLAY===", num_games)

            if number_of_timeslots >= num_games:
                self.generate_games(tournament)
                return HttpResponseRedirect("/tournaments/" + str(tournament_pk) + "/")
            messages.error(request, "Could not create games!")
            return HttpResponseRedirect("/tournaments/" + str(tournament_pk) + "/")
        except Tournament.DoesNotExist:
            raise Http404

    # ficaste aqui verifica o n de jogos jogados
    def generate_games(self, tournament):
        teams = tournament.team_set.all()
        print("teams_count===", teams.count())
        try:
            with transaction.atomic():
                for k in range(tournament.number_of_hands):
                    for i in range(teams.count() - 1):
                        # getting the number of games team_a already has, by checking how many times
                        # team_a is registered as home_team or away_team in this tournament
                        num_games_team_a = tournament.game_set.filter(
                            Q(home_team__pk=teams[i].pk) | Q(away_team__pk=teams[i].pk)
                        ).count()
                        # checking if team_a already has all it's games scheduled
                        if num_games_team_a < (
                            (teams.count() - 1) * tournament.number_of_hands
                        ):
                            for j in range(i + 1, teams.count()):
                                print("j=", j)
                                num_games_team_b = tournament.game_set.filter(
                                    Q(home_team__pk=teams[j].pk)
                                    | Q(away_team__pk=teams[j].pk)
                                ).count()
                                if num_games_team_b < (
                                    (teams.count() - 1) * tournament.number_of_hands
                                ):
                                    random_timeslots = (
                                        TimeSlot.objects.filter(
                                            tournament__pk=tournament.pk
                                        )
                                        .filter(isFree=True)
                                        .order_by("?")
                                    )
                                    if random_timeslots.count() > 0:
                                        timeslot = random_timeslots.first()
                                        timeslot.isFree = False
                                        timeslot.title = (
                                            str(teams[i]) + " vs " + str(teams[j])
                                        )
                                        timeslot.description = (
                                            "Field="
                                            + str(timeslot.field)
                                            + "\nGame Date= "
                                            + str(timeslot.start_time.day)
                                            + "\nGame Time= "
                                            + str(timeslot.start_time.time)
                                            + " : "
                                            + str(timeslot.end_time.time)
                                        )
                                        timeslot.save()
                                        aux_choice = randint(0, 1)
                                        if aux_choice == 0:
                                            home_team = teams[i]
                                            away_team = teams[j]
                                        else:
                                            home_team = teams[j]
                                            away_team = teams[i]
                                        print("DAY===", timeslot.start_time.day)
                                        aux_day = Day.objects.create(
                                            day=timeslot.start_time
                                        )
                                        game = Game.objects.create(
                                            cost=timeslot.field.cost,
                                            gameDate=aux_day,
                                            tournament=tournament,
                                            timeslot=timeslot,
                                            home_team=home_team,
                                            away_team=away_team,
                                        )
                                        game.save()
        except IntegrityError:
            pass
        print("ALL CREATED GAMES====", tournament.game_set.all())
        print("THEIR COUNT===", tournament.game_set.all().count())
        return


class RestResults(generics.RetrieveUpdateAPIView):
    queryset = Result.objects.all()
    serializer_class = ResultSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        try:
            with transaction.atomic():
                instance.home_score = instance.goal_set.filter(is_home=True).count()
                instance.away_score = instance.goal_set.filter(is_away=True).count()
                instance.save()
        except IntegrityError:
            pass
        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)


class RestTournaments(generics.RetrieveUpdateAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [IsAuthenticated]


class RestTeams(generics.RetrieveUpdateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]


class notifyTeam(generics.RetrieveUpdateAPIView):
    queryset = TeamUser.objects.all()
    serializer_class = TeamUserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        teampk = kwargs.pop("teampk", False)

        instance = TeamUser.objects.filter(team=teampk)
        notification_info = '<ul id="ul_users" class="list-group margin" style="width: 45vw; height: 20vw; overflow: auto;">'
        for i, elem in enumerate(instance):
            notification_info += (
                '<li class="groupList list-group-item">'
                + str(i)
                + " - "
                + elem.player.first_name
                + " "
                + elem.player.last_name
                + " "
                + elem.player.username
                + " - "
                + elem.position.name.split(" ")[0]
                + "</li>"
            )
        notification_info += "</ul>"
        for elem in instance:

            Notifications.objects.create(
                title="STARTING 11 FOR NEXT GAME IN TEAM " + elem.team.name,
                description=notification_info,
                user_send=elem.player,
                origin="Captain",
            ).save()

        return Response("Done")


class replaceMember(generics.RetrieveUpdateAPIView):
    queryset = TeamUser.objects.all()
    serializer_class = TeamUserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        teampk = kwargs.pop("teampk", False)
        user = request.user
        instance = TeamUser.objects.filter(team=teampk).filter(player=user).first()

        findCaptain = (
            TeamUser.objects.filter(team=teampk).filter(isCaptain=True).first()
        )
        name = request.data["name"]
        email = request.data["email"]
        phone = request.data["phone"]
        until = request.data["until"]

        Notifications.objects.create(
            title="USER ADD A SUBSTITUTE",
            description="<h3>The user "
            + request.user.username
            + " is going to add an annonimous user to replace him <br>"
            + " This info is the following:<br>"
            + "Name: "
            + name
            + "<br>"
            + "Email: "
            + email
            + "<br>"
            + "Phone: "
            + str(phone)
            + "<br>"
            + " He is going to replace untit "
            + str(until)
            + "</h3>",
            user_send=findCaptain.player,
            origin="Player - " + str(instance.player),
        ).save()

        return Response("Done")


class replaceSubseserve(APIView):
    queryset = Team.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [IsAuthenticated]
    allowed_methods = "PATCH"

    def patch(self, request, *args, **kwargs):

        user = request.data["user"]
        replace = request.data["replace"]
        team = request.data["team"]

        instance = CustomUser.objects.get(pk=user)
        instance2 = CustomUser.objects.get(pk=replace)
        instance3 = Team.objects.get(pk=team)

        Notifications.objects.create(
            title="Replace a player in tournament ",
            description="<h3>You are going to replace the user "
            + instance.username
            + " in the team "
            + instance3.name
            + " from the tournament "
            + instance3.tournament.name
            + ".</h3>",
            user_send=instance2,
            origin="System",
        ).save()

        return Response("Done")


class addReserve(APIView):

    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [IsAuthenticated]
    allowed_methods = "PATCH"

    def patch(self, request, *args, **kwargs):
        tournamentpk = kwargs.pop("tournamentpk", False)

        instance = Tournament.objects.get(pk=tournamentpk)
        listReserves = instance.reserves
        listReserves.add(request.user)
        instance.save()

        print("Chegou")
        Notifications.objects.create(
            title="NEW RESERVE IN YOUT TOURNAMENT " + instance.name,
            description="<h3>The user "
            + request.user.username
            + " as know as "
            + request.user.first_name
            + " "
            + request.user.last_name
            + " is a new reserve for your tournament.</h3>",
            user_send=instance.tournament_manager,
            origin="System",
        ).save()

        return Response("Done")


class changeInfo(generics.RetrieveUpdateAPIView):
    queryset = TeamUser.objects.all()
    serializer_class = TeamUserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        teampk = kwargs.pop("teampk", False)
        playerpk = kwargs.pop("playerpk", False)
        print(request.data)
        budget = request.data["budget"]
        absences = request.data["absences"]

        instance = TeamUser.objects.filter(player=playerpk).filter(team=teampk).first()
        try:
            with transaction.atomic():
                user = instance.player
                user.hierarchy += int(absences)
                user.save()
        except IntegrityError:
            pass
        serializer = self.get_serializer(
            instance, {"budget": budget, "absences": absences}, partial=True
        )

        Notifications.objects.create(
            title="Change budget and absences in team " + instance.team.name,
            description="<h3>Hey I'm the captain from "
            + instance.team.name
            + ", I just updated your budget to "
            + budget
            + " euros and absences to "
            + absences
            + ".</h3>",
            user_send=instance.player,
            origin="Captain",
        ).save()

        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        if getattr(instance, "_prefetched_objects_cache", None):
            instance._prefetched_objects_cache = {}
        return Response("Done")


class changePos(generics.RetrieveUpdateAPIView):
    queryset = TeamUser.objects.all()
    serializer_class = TeamUserSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        teampk = kwargs.pop("teampk", False)
        playerpk = kwargs.pop("playerpk", False)

        instance = TeamUser.objects.filter(player=playerpk).filter(team=teampk).first()
        position_name = instance.position.name.split(" ")[0]

        if instance.position.start == False:
            team = Team.objects.get(pk=teampk)
            tactic = Tactic.objects.get(pk=team.tactic.pk)
            positions2replace = list(
                tactic.positions.filter(
                    name__icontains=instance.position.name.split(" ")[0]
                )
            )

            for user in team.teamuser_set.all():
                if user.position in positions2replace:
                    for i in range(len(positions2replace)):
                        if user.position.name == positions2replace[i].name:
                            del positions2replace[i]
                            break
            if len(positions2replace) > 0:
                position_name = positions2replace[0].name
                instance2 = Position.objects.filter(name="none")
            else:
                instance2 = (
                    TeamUser.objects.filter(team=teampk)
                    .filter(
                        position__name__contains=instance.position.name.split(" ")[0]
                    )
                    .filter(~Q(player=instance.player))
                )

        else:

            instance2 = TeamUser.objects.filter(team=teampk).filter(
                position__name=position_name
            )

        if not instance2.exists():
            getPosition = (
                Position.objects.filter(~Q(start=instance.position.start))
                .filter(name__icontains=position_name)
                .first()
            )
            serializer = self.get_serializer(
                instance, {"position": getPosition.pk}, partial=True
            )

            Notifications.objects.create(
                title="Change Position in team " + instance.team.name,
                description="<h3>Hey I'm the captain from "
                + instance.team.name
                + ", I just changed your position to "
                + getPosition.name
                + ".</h3>",
                user_send=instance.player,
                origin="Captain",
            ).save()
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            if getattr(instance, "_prefetched_objects_cache", None):
                instance._prefetched_objects_cache = {}
            return Response("Done")
        else:
            instance2 = instance2.first()

            position1 = instance.position
            position2 = instance2.position

            serializer = self.get_serializer(
                instance, {"position": position2.pk}, partial=True
            )
            serializer2 = self.get_serializer(
                instance2, {"position": position1.pk}, partial=True
            )
            Notifications.objects.create(
                title="Change Position in team " + instance.team.name,
                description="<h3>Hey I'm the captain from "
                + instance.team.name
                + ", I just changed your position to "
                + position2.name
                + ".</h3>",
                user_send=instance.player,
                origin="Captain",
            ).save()
            Notifications.objects.create(
                title="Change Position in team " + instance2.team.name,
                description="<h3>Hey I'm the captain from "
                + instance2.team.name
                + ", I just changed your position to "
                + position1.name
                + ".</h3>",
                user_send=instance2.player,
                origin="Captain",
            ).save()
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            serializer2.is_valid(raise_exception=True)
            self.perform_update(serializer2)

            return Response("Done")


class RestTeamUserView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TeamUser.objects.all()
    serializer_class = TeamUserSerializer
    permission_classes = [IsAuthenticated]


class RestListTournaments(generics.ListAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

    def list(self, request, *args, **kwarg):
        queryset = self.filter_queryset(self.get_queryset())
        params = request.query_params
        if params["name"] != "":
            queryset = queryset.filter(name__icontains=params["name"])
        print("SET?===", queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.isConfirmed = True
        host = request.get_host()
        ask_admin_for_permissions.apply_async((host, uid))
        messages.info(
            request, "Confirmed. The Admin is now going to activate your account."
        )
        return HttpResponseRedirect(reverse("main:landing-page"))
    else:
        return HttpResponse("Activation link is invalid!")


@user_passes_test(lambda u: u.is_superuser)
def validate(request, pk):
    user = (
        CustomUser.objects.filter(pk=pk)
        .filter(is_active=False)
        .filter(isConfirmed=True)
        .first()
    )
    serializer = PartialCustomUserSerializer(user)
    if user:
        return render(
            request,
            template_name="main/admin_validation.html",
            context={"user": serializer.data},
        )
    else:
        messages.error(request, "User Not Found")
        return render(request, template_name="main/admin_validation.html")


def validateMultiple(request):
    users = CustomUser.objects.filter(is_active=False).filter(isConfirmed=True)
    serializer = PartialCustomUserSerializer(users, many=True)
    if users.exists():
        return render(
            request,
            queryset=CustomUser.objects.all(),
            template_name="main/admin_validation_multiple.html",
            context={"users": serializer.data},
        )
    else:
        messages.error(request, "No users Found")
        return render(request, template_name="main/admin_validation.html")


class RestUsers(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]
    queryset = CustomUser.objects.all()


class RestUsersListPatch(APIView):
    allowed_methods = "PATCH"
    # authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]
    queryset = CustomUser.objects.all()

    def patch(self, request):
        data = request.data
        print(data)
        try:
            for elem in request.data:
                instance = CustomUser.objects.get(pk=list(elem.keys())[0])
                serializer = CustomUserSerializer(
                    instance, data=list(elem.values())[0], partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
            return Response("success")
        except Exception as exp:
            print("exp::", exp)
            raise exp


class RestGoals(generics.DestroyAPIView):
    queryset = Goal.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]


class RestUsersList(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        params = request.query_params
        queryset = queryset.annotate(
            search_name=Concat("first_name", V(" "), "last_name")
        ).filter(
            Q(search_name__icontains=params["name"])
            | Q(first_name__icontains=params["name"])
            | Q(last_name__icontains=params["name"])
        )
        print("SET?===", queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class RestCaptainsList(RestUsers):
    queryset = TeamUser.objects.filter(isCaptain=True)

    def list(self, request, tournamentId):

        q_set = TeamUser.objects.filter(isCaptain=True).team(
            tournament__pk=tournamentId
        )
        print(q_set)
        page = self.paginate_queryset(q_set)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(q_set, many=True)
        return Response(serializer.data)


class RestTeamsList(generics.ListAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        params = request.query_params
        for key in params.keys():
            if key == "name":
                queryset = queryset.filter(name__icontains=params[key])
            if key == "tournament_pk":
                queryset = queryset.filter(tournament__pk=params[key])

        queryset = (
            queryset.annotate(q_count=Count("teamuser"))
            .order_by("-q_count")
            .filter(q_count__lte=15)
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AdminMenuView(generic.TemplateView):
    template_name = "main/adminMenu.html"

    def get(self, request):
        if request.user.is_superuser == True:
            users = CustomUserSerializer(CustomUser.objects.all(), many=True)
            teams = TeamSerializer(Team.objects.all(), many=True)
            tournaments = TournamentSerializer(Tournament.objects.all(), many=True)
            return render(
                request,
                template_name=self.template_name,
                context={
                    "users": users.data,
                    "teams": teams.data,
                    "tournaments": tournaments.data,
                },
            )
        else:
            raise Http404


class TournamentDetailsView(generic.View):
    def get(self, request, pk):
        try:
            teams_data = Team.objects.filter(tournament__id=pk)
            scorers = None
            teams = []
            tournament = Tournament.objects.get(pk=pk)
            ready_to_start = self.check_start_status(tournament)
            if tournament.game_set.all().count() > 0:
                for elem in teams_data:
                    (
                        games_won,
                        goals_scored,
                        tied_games,
                        lost_games,
                        goals_conceded,
                    ) = self.get_games_won_goals_scored(elem, tournament)
                    # print(elem.name)
                    teams.append(
                        {
                            "id": elem.pk,
                            "name": elem.name,
                            "points": (games_won * 3 + tied_games),
                            "goals_scored": goals_scored,
                            "games_won": games_won,
                            "tied_games": tied_games,
                            "games_lost": lost_games,
                            "goals_conceded": goals_conceded,
                        }
                    )
                # tournament = TournamentSerializer(Tournament.objects.get(pk=pk)).data
                scorers = self.get_top_scorers(tournament)
            else:
                for elem in teams_data:
                    teams.append(
                        {
                            "id": elem.pk,
                            "name": elem.name,
                            "points": 0,
                            "goals_scored": 0,
                            "games_won": 0,
                            "tied_games": 0,
                            "games_lost": 0,
                            "goals_conceded": 0,
                        }
                    )
            print("teams===", teams)
            print("ready-to_start==", ready_to_start)
            teams = sorted(teams, key=itemgetter("points", "goals_scored"))
            teams.reverse()
            return render(
                request,
                template_name="main/tournamentDetails.html",
                context={
                    "tournament": tournament,
                    "teams": teams,
                    "scorers": scorers,
                    "ready_to_start": ready_to_start,
                },
            )
        except (Team.DoesNotExist, Tournament.DoesNotExist):
            return JsonResponse(
                {"teams": ["Nothing was Found"], "tournament": ["Nothing Was Found"]}
            )

    def get_games_won_goals_scored(self, team, tournament):
        games_won = 0
        goals_scored = 0
        goals_conceded = 0
        tied_games = 0
        games_lost = 0
        games = tournament.game_set.all()
        for elem in games:

            res_set = elem.result_set.all()
            home = False
            away = False
            first_res = res_set.first()
            second_res = res_set.last()

            if first_res == None or second_res == None:
                return games_won, goals_scored, tied_games, games_lost, goals_conceded
            print("fr===", first_res)
            print("sr===", second_res)
            if first_res == None or second_res == None:
                return games_won, goals_scored, tied_games, games_lost, goals_conceded

            if (
                first_res.game.home_team == team.name
                and second_res.game.home_team == team.name
            ):
                home = True
            elif (
                first_res.game.away_team == team.name
                and second_res.game.away_team == team.name
            ):
                away = True
            if home or away:
                if (
                    first_res.home_score == second_res.home_score
                    and first_res.away_score == second_res.away_score
                ):
                    if home:
                        goals_scored += first_res.home_score
                        goals_conceded += first_res.away_score
                        if first_res.home_score > first_res.away_score:
                            games_won += 1
                        elif first_res.home_score < first_res.away_score:
                            games_lost += 1
                        else:
                            tied_games += 1
                    elif away:
                        goals_scored += first_res.away_score
                        goals_conceded += first_res.home_score
                        if first_res.away_score > first_res.home_score:
                            games_won += 1
                        elif first_res.away_score < first_res.home_score:
                            games_lost += 1
                        else:
                            tied_games += 1
        return games_won, goals_scored, tied_games, games_lost, goals_conceded

    def get_top_scorers(self, tournament):
        teams_pks = Team.objects.filter(tournament__pk=tournament.pk).values_list("pk")
        tournament_users = TeamUser.objects.filter(team__pk__in=teams_pks)
        # create lists and order them by count
        # ordered_list = sorted(tournament_users, key=tournament_users.goal_set.all().count())
        ordered_list = {}
        for user in tournament_users:
            print(user.player.username)
            ordered_list[user.player.username] = 0
            goals = user.goal_set.all()
            for goal in goals:
                if goal.result:
                    if goal.result.is_final:
                        ordered_list[user.player.username] += 1
        ordered_list = dict(sorted(ordered_list.items()))

        return ordered_list

    def check_start_status(self, tournament):
        teams = Team.objects.filter(tournament__pk=tournament.pk)
        print("TEAMS COUNT===", teams.count())
        if teams.count() < tournament.number_teams:
            return False
        else:
            count = 0
            for team in teams:
                print("team_users===", team.teamuser_set.count())
                print("num_players===", team.numberPlayers)
                if team.teamuser_set.all().count() == team.numberPlayers:
                    count += 1
            print("COUNT===", count)
            if count == tournament.number_teams:
                return True
        return False


class CalendarView(BaseCalendarView):
    model = TimeSlot
    template_name = "main/calendar.html"
    queryset = TimeSlot.objects.all()
    allow_future = True

    def get(self, request, *args, **kwargs):
        try:
            self.date_list, self.object_list, extra_context = self.get_dated_items()
            context = self.get_context_data(
                object_list=self.object_list, date_list=self.date_list, **extra_context
            )
            return self.render_to_response(context)
        except Http404:
            messages.error(request, "Ainda não há jogos!")
            return render(request, "main/calendar.html")

    def get_queryset(self):
        """
        Return the list of items for this view.
        The return value must be an iterable and may be an instance of
        `QuerySet` in which case `QuerySet` specific behavior will be enabled.
        """

        if self.queryset is not None:
            # filter o queryset de acordo com os parametros
            filter = self.kwargs["filter"]

            # se o parametro filter== 'all' e o pk==0, devolver todos os jogos
            try:
                if filter != "all":
                    # se o filter =="team", devolver os jogos da equipa cujo pk==pk
                    if filter == "team":
                        pk = int(self.kwargs["pk"])
                        team_games = Game.objects.filter(
                            Q(home_team__pk=pk) | Q(away_team__pk=pk)
                        ).values_list("id")
                        queryset = TimeSlot.objects.filter(
                            game__pk__in=team_games
                        ).order_by("start_time")
                    elif filter == "tournament":
                        # se o filter=="tournament", devolver os jogos do tourneio gujo pk==pk
                        pk = int(self.kwargs["pk"])
                        tournament_games = Tournament.objects.get(
                            pk=pk
                        ).game_set.values_list("id")
                        queryset = TimeSlot.objects.filter(
                            game__pk__in=tournament_games
                        ).order_by("start_time")
                    else:
                        raise Http404
                else:
                    pk = int(self.kwargs["pk"])
                    if pk == 0:
                        queryset = self.queryset
                    else:
                        raise Http404
            except (Tournament.DoesNotExist, Team.DoesNotExist, TimeSlot.DoesNotExist):
                raise Http404
            if isinstance(queryset, QuerySet):
                queryset = queryset.all()
        elif self.model is not None:
            queryset = self.model._default_manager.all()
        else:
            raise ImproperlyConfigured(
                "%(cls)s is missing a QuerySet. Define "
                "%(cls)s.model, %(cls)s.queryset, or override "
                "%(cls)s.get_queryset()." % {"cls": self.__class__.__name__}
            )
        ordering = self.get_ordering()
        if ordering:
            if isinstance(ordering, str):
                ordering = (ordering,)
            queryset = queryset.order_by(*ordering)
        return queryset

    def get_year(self):
        """Return the year for which this view should display data."""
        year = self.year
        if year is None:
            try:
                year = year = date.today().year
                print("YEAR", year)
            except Exception:
                try:
                    year = self.request.GET["year"]
                except KeyError:
                    raise Http404(_("No year specified"))
        return year

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # use today's date for the calendar
        d = get_date(self.request.GET.get("month", None))
        filter = self.kwargs["filter"]
        pk = int(self.kwargs["pk"])
        print("DATE===", d)
        # Instantiate our calendar class with today's year and date
        cal = Calendar(d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        context["calendar"] = mark_safe(html_cal)
        context["prev_month"] = prev_month(d)
        context["next_month"] = next_month(d)

        print("CONTEXT===", context)
        return context


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = "month=" + str(prev_month.year) + "-" + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = "month=" + str(next_month.year) + "-" + str(next_month.month)
    return month


def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split("-"))
        return date(year, month, day=1)
    return datetime.today()


def nCr(n, r):
    f = math.factorial
    return f(n) / f(r) / f(n - r)


class GameView(generics.CreateAPIView):
    model = Game
    template_name = "main/game.html"

    def get_form(
        self,
        pk,
        is_home_captain,
        is_away_captain,
        is_tournament_manager,
        form_class=None,
    ):

        """Return an instance of the form to be used in this view."""

        form_class, form_class2 = self.get_form_class(
            pk, is_home_captain, is_away_captain, is_tournament_manager
        )
        if form_class2:
            return form_class(), form_class2()
        else:
            return form_class(), form_class2

    def get_form_class(
        self, pk, is_home_captain, is_away_captain, is_tournament_manager
    ):
        """
        The form can only show the workouts belonging to the user.

        This is defined here because only at this point during the request
        have we access to the current user
        """
        game = Game.objects.get(pk=pk)
        home_team = game.home_team
        away_team = game.away_team

        q_set = None
        if is_home_captain or is_tournament_manager:
            q_set = Goal.objects.filter(result__game__home_team__pk=home_team.pk)
        elif is_away_captain:
            q_set = Goal.objects.filter(result__game__away_team__pk=away_team.pk)

        if q_set:

            class StepFormRemoveGoals(forms.Form):
                goal_set = forms.ModelChoiceField(queryset=q_set)

            form2 = StepFormRemoveGoals

        else:
            form2 = None

        class StepForm(GoalForm):
            scorer = forms.ModelChoiceField(
                queryset=TeamUser.objects.filter(
                    Q(team_id=home_team.pk) | Q(team_id=away_team.pk)
                )
            )

        return StepForm, form2

    def get(self, request, pk):
        try:
            pk = int(pk)
            selected_game = Game.objects.filter(pk=pk).first()

        except (ValueError, Game.DoesNotExist):
            selected_game = None

        if selected_game:
            today = timezone.now()
            print("TIMESLOT===", selected_game.timeslot.start_time)
            print("now===", today)
            done = selected_game.timeslot.start_time < today

            print("HERERERERE===", done)
            if done:
                final_score = selected_game.result_set.all()
                print("FINAL SCORE===", final_score.count())
                if final_score.count() == 2:

                    if compareResults(final_score.first(), final_score.last()):
                        print(
                            "_________________________________________________________________"
                        )
                        final_score.first().is_final = True
                        final_score.first().save()
                        if selected_game:
                            print("FDSFSDSFDSFSDSFDS")
                            return render(
                                request,
                                template_name=self.template_name,
                                context={"game": selected_game, "result": final_score},
                            )
                        raise Http404(("Game Does Not Exist"))
                    else:
                        # mandar notify ao admin - dar o link onde ele pode editar o resultado!
                        Notifications.objects.get_or_create(
                            title="The game "
                            + selected_game.timeslot.title
                            + " has conflicts in the results set by both captains.",
                            description="<h3>There was a conflict in the final score of "
                            + str(selected_game.home_team)
                            + " vs "
                            + str(selected_game.away_team)
                            + " in tournament"
                            + selected_game.tournament.name
                            + "</h3><h3>Please Confirm the Correct Result</h3>",
                            user_send=selected_game.tournament.tournament_manager,
                            html='<button type="button" class="btn btn-dark" onclick=window.location.href="/games/'
                            + str(selected_game.pk)
                            + '/">Verify Result</button>',
                            origin="Captain",
                        )
                        messages.error(
                            request,
                            "Erros no resultado. Para apurar o resultado definitivo, por favor contacte o Gestor de Torneio",
                        )
                print("OIOI")
                home_captain = selected_game.home_team.teamuser_set.filter(
                    isCaptain=True
                ).first()
                print("HOME CAPTAIN===", home_captain)
                away_captain = selected_game.away_team.teamuser_set.filter(
                    isCaptain=True
                ).first()
                print("AWAY CAPTAIN===", away_captain)
                # tratar do caso em que n ha capitao
                is_home_captain = False
                is_away_captain = False
                is_tournament_manager = False
                if request.user.pk == home_captain.player.pk:
                    is_home_captain = True
                    result = selected_game.result_set.filter(
                        captain__pk=home_captain.pk
                    ).first()
                elif request.user.pk == away_captain.player.pk:
                    is_away_captain = True
                    result = selected_game.result_set.filter(
                        captain__pk=away_captain.pk
                    ).first()

                elif request.user.pk == selected_game.tournament.tournament_manager.pk:
                    is_tournament_manager = True
                    result = selected_game.result_set.filter(
                        captain__pk=home_captain.pk
                    ).first()
                    print("IS TM===", result)
                else:
                    result = None

                form, form2 = self.get_form(
                    pk, is_home_captain, is_away_captain, is_tournament_manager
                )
                print("FORM===", form)
                print("FORM2===", form2)
                return render(
                    request,
                    template_name=self.template_name,
                    context={
                        "game": selected_game,
                        "form": form,
                        "form2": form2,
                        "is_home_captain": is_home_captain,
                        "is_away_captain": is_away_captain,
                        "is_tournament_manager": is_tournament_manager,
                        "result": result,
                    },
                )
                raise Http404
            else:
                return render(
                    request,
                    template_name=self.template_name,
                    context={"game": selected_game},
                )
        else:
            return HttpResponse("NO GAME DEFINED")

    def post(self, request, pk):
        """
        Overriting the default post made by html form
        """
        try:
            pk = int(pk)
            selected_game = Game.objects.filter(pk=pk).first()

        except (ValueError, Game.DoesNotExist):
            selected_game = None
        print("ole===", request.data)
        serializer = GoalSerializer(data=request.data)
        if serializer.is_valid():
            goal = serializer.save()
        else:
            messages.error(request, serializer.errors)
            return HttpResponseRedirect("")

        if selected_game:
            # searching for the captain in the home team
            tournament_manager = False
            captain = False
            if request.user.pk == selected_game.tournament.tournament_manager.pk:
                tournament_manager = True
                print("TM==", tournament_manager)

            if tournament_manager:
                captain = selected_game.home_team.teamuser_set.filter(
                    isCaptain=True
                ).first()
                print("TM_CAP===", captain)
            else:
                if not selected_game.result_set.filter(is_final=True).exists():
                    print("HERERERE")
                    captain = selected_game.home_team.teamuser_set.filter(
                        player__pk=request.user.pk
                    ).first()
                    print("captain==", captain)
                    # searching for the captain in the away team
                    if not captain:
                        captain = selected_game.away_team.teamuser_set.filter(
                            player__pk=request.user.pk
                        ).first()
                        print("captain2==", captain)
            if captain:
                result = selected_game.result_set.filter(captain__pk=captain.pk).first()

                if not result:
                    result = Result.objects.create(
                        home_score=0, away_score=0, captain=captain, game=selected_game
                    )

                goal.result = result

                # checking if the scorer belongs to the home team
                home_player = selected_game.home_team.teamuser_set.filter(
                    pk=goal.scorer.pk
                ).exists()
                # checking if the scorer belongs to the away team
                if not home_player:
                    away_player = selected_game.away_team.teamuser_set.filter(
                        pk=goal.scorer.pk
                    ).exists()
                if home_player or away_player:
                    # incrementing and saving the result accordingly
                    if home_player:

                        goal.is_home = True
                    else:
                        goal.is_away = True
                    goal.save()
                    result.home_score = result.goal_set.filter(is_home=True).count()
                    result.away_score = result.goal_set.filter(is_away=True).count()
                    if tournament_manager:
                        result.is_final = True
                    result.save()
                    return Response("success")
                else:
                    messages.error(
                        request,
                        "This player does not play for any of the teams in this game",
                    )
                    return HttpResponseRedirect("")
            else:
                return HttpResponseBadRequest(
                    "You can't create this result! Your tournament manager is now responsible for this."
                )
        else:
            raise Http404
