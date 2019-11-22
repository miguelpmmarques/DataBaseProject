import json

from operator import itemgetter
import calendar
from datetime import datetime, date, timedelta

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
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.db import transaction
from django.db import IntegrityError
from django.db.models import Q
from django.db.models import Value as V
from django.db.models.functions import Concat
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.forms import AuthenticationForm


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
from .serializers import PositionSerializer

from .tokens import account_activation_token
from .tasks import ask_admin_for_permissions
from .forms import CustomUserForm
from .forms import TournamentCreationForm
from .forms import TeamCreationForm
from .forms import PositionsForm


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
from .models import Position
from .models import Result
from .models import Game
from .models import TimeSlot

from .utils import Calendar
from django.utils.safestring import mark_safe


from time import sleep

from django.views.generic.dates import YearArchiveView

from .models import Game

# TINYURL.COM/SISTEMAS19


class BaseCalendarView(YearArchiveView):
    model = TimeSlot
    date_field = "start_time"
    make_object_list = True
    template_name = "main/calendar.html"


# Create your views here.


class GoToTeamFromPlayer(generic.DetailView):
    template_name = "main/goToTeamFromPlayer.html"

    def get(self, request):

        teamuser = TeamUser.objects.all().order_by("-player")
        return render(
            request, template_name=self.template_name, context={"users": teamuser},
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

        return render(
            request,
            template_name=self.template_name,
            context={
                "captain": CustomUser.objects.get(
                    pk__in=list(
                        TeamUser.objects.filter(team__pk=team_selected.pk)
                        .filter(isCaptain=True)
                        .values_list("player", flat=True)
                    )
                ),
                "myTeam": team_selected,
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
            },
        )
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
        return HttpResponseRedirect(reverse("main:login"))


class ProfileView(generic.DetailView):
    template_name = "main/profile.html"
    model = CustomUser


class ProfileView(generic.DetailView):
    template_name = "main/profile.html"
    model = CustomUser


class CreateTeam(generic.CreateView):
    template_name = "main/createTeam.html"
    form_class = TeamCreationForm

    def get(self, request):
        if request.user.is_authenticated:
            return render(
                request,
                template_name=self.template_name,
                context={"form": self.form_class},
            )
        return HttpResponseRedirect(reverse("main:landing-page"))

    def post(self, request):
        """
        overriding native post method, for e-mail sending with token verification
        """
        user = request.user
        if user.is_authenticated:
            form = TeamCreationForm(request.POST)
            if form.is_valid():
                team = form.save(commit=False)
                request.session["team_form"] = TeamSerializer(team).data
                return redirect("/team/apply/0/")

            return HttpResponse("Please Fill all Fields")
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
            team_exists = Team.objects.get(pk=pk)
        except Position.DoesNotExist:
            raise Http404
        except Team.DoesNotExist:
            team_serialized = request.session["team_form"]
            team = TeamSerializer(data=team_serialized)
            team_serialized = request.session["team_form"]
            if team.is_valid(raise_exception=True):
                print("GUARDOU")
                new_team = team.save()
                TeamUser.objects.create(
                    isCaptain=True,
                    player=request.user,
                    team=new_team,
                    position=position,
                ).save()
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
                    + ". I wish you the best of luck in the matches!</h3>",
                    user_send=request.user,
                    origin="Tournament Manager",
                ).save()
                return Response("success")
            else:
                print("\n\n" + team.errors)
        TeamUser.objects.create(
            isCaptain=False, player=request.user, team=team_exists, position=position,
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
        try:
            tournaments = Tournament.objects.all()
            teams = Team.objects.all()
            return render(
                request,
                template_name=self.template_name,
                context={"teams": teams, "tournaments": tournaments},
            )

        except (Tournament.DoesNotExist, Team.DoesNotExist) as err:
            raise Http404


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
    template_name = "main/createTeam.html"

    def get(self, request):
        team = Team.objects.all()
        tactics = Tactic.objects.all()
        tournaments = Tournament.objects.all()
        # print(tournaments)
        # print(tactics)
        # print(team)
        return render(
            request, template_name=self.template_name, context={"tournaments": tournaments, "tactics":tactics},
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
            messages.error(request, "Invalid username or password")
            return HttpResponseRedirect("")


class RegisterView(generic.CreateView):
    form_class = CustomUserForm
    success_url = reverse_lazy("login")
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
                + " has registered and would like to become a member of Unileague</h3><br><h3>"
                + "</h3> <button class='btn btn-light btn-outline-secondary' id='activate_user'><span id='spinner' class='spinner-border spinner-border-sm' hidden='true'></span>ACTIVATE</button>",
                user_send=superuser,
                origin="System",
            ).save()
            Notifications.objects.create(
                title="WELCOME TO UNILEAGUE",
                description="Welcome "
                + user.first_name
                + " "
                + user.last_name
                + " to the best soccer app in the world, join/create a team a start playing!",
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
            messages.error(request, "Waiting for admin's confirmation...")
            return HttpResponseRedirect("")
        messages.error(request, form.errors)
        return HttpResponseRedirect(reverse("main:landing-page"))


"""<h1>The User {{user.username}} has registered and would like to become a member of Unileague</h1>
<br>
<h2>{{user.first_name}} {{user.last_name}}</h2>
<ul id="user_info_{{user.pk}}">
    {% for k,v in user.items %}
    {% ifnotequal k 'id' %}
    {% ifnotequal k 'first_name' %}
    {% ifnotequal k 'last_name' %}
    <li>{{k}}: {{v}}</li>
    {% endifnotequal %}
    {% endifnotequal %}
    {% endifnotequal %}
    {% endfor %}
</ul>
"""


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
        "beginTournament": {
            "value": "Begining of Tournament",
            "type": "datetime-local",
        },
        "endTournament": {"value": "End of Tournament", "type": "datetime-local"},
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
                    for elem in dates[0].split(","):
                        try:
                            day = Day.objects.get(day=elem)
                        except Day.DoesNotExist:
                            day = Day.objects.create(day=elem)
                        data_copy.update({k: day.pk})
            data_copy.update({"tournament_manager": request.user.pk})
            data_copy.update({"fields": 1})
            serializer = TournamentSerializer(data=data_copy)
            if serializer.is_valid():
                serializer.save()
                return Response({"sucess": True})
            return Response({"errors": serializer.errors})
        else:
            return HttpResponseRedirect(reverse("main:landing-page"))


class RestTournaments(generics.RetrieveUpdateAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [IsAuthenticated]


class RestTeams(generics.RetrieveUpdateAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
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
        return HttpResponse(
            "Thank you for your email confirmation. Now you can login your account."
        )
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
        raise Http404


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
        raise Http404


class RestUsers(generics.RetrieveUpdateAPIView):
    serializer_class = CustomUserSerializer
    permission_classes = [IsAuthenticated]


class RestUsersListPatch(APIView):
    allowed_methods = "PATCH"
    # authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

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

            teams = []
            tournament = Tournament.objects.get(pk=pk)
            for elem in teams_data:
                (
                    games_won,
                    goals_scored,
                    tied_games,
                    lost_games,
                ) = self.get_games_won_goals_scored(elem, tournament)
                teams.append(
                    {
                        "id": elem.pk,
                        "name": elem.name,
                        "points": (games_won * 3 + tied_games),
                        "goals_scored": goals_scored,
                    }
                )
            # tournament = TournamentSerializer(Tournament.objects.get(pk=pk)).data
            print("teams===", teams)
            teams = sorted(teams, key=itemgetter("points", "goals_scored"))
            return render(
                request,
                template_name="main/tournamentDetails.html",
                context={"tournament": tournament, "teams": teams},
            )
        except (Team.DoesNotExist, Tournament.DoesNotExist):
            return JsonResponse(
                {"teams": ["Nothing was Found"], "tournament": ["Nothing Was Found"]}
            )

    def get_games_won_goals_scored(self, team, tournament):
        games_won = 0
        goals_scored = 0
        tied_games = 0
        lost_games = 0
        games = tournament.game_set.all()
        for elem in games:
            res_set = elem.result_set.all()
            home = False
            away = False
            first_res = res_set.first()
            second_res = res_set.last()
            if first_res.home_team == team.name and second_res.home_team == team.name:
                home = True
            elif first_res.away_team == team.name and second_res.away_team == team.name:
                away = True
            if home or away:
                if (
                    first_res.home_score == second_res.home_score
                    and first_res.away_score == second_res.away_score
                ):
                    if home:
                        goals_scored += first_res.home_score
                        if first_res.home_score > first_res.away_score:
                            games_won += 1
                        elif first_res.home_score < first_res.away_score:
                            games_lost += 1
                        else:
                            tied_games += 1
                    elif away:
                        goals_scored += first_res.away_score
                        if first_res.away_score > first_res.home_score:
                            games_won += 1
                        elif first_res.away_score < first_res.home_score:
                            games_lost += 1
                        else:
                            tied_games += 1
        return games_won, goals_scored, tied_games, lost_games


class CalendarView(BaseCalendarView):
    model = TimeSlot
    template_name = "main/calendar.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # use today's date for the calendar
        d = get_date(self.request.GET.get("month", None))
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


class GameView(generic.DetailView):
    model = Game
    template_name = "main/game.html"

    def get(self, request, pk):
        try:
            pk = int(pk)
            selected_game = Game.objects.filter(pk=pk).first()
        except ValueError:
            team_selected = None

        selected_game = Game.objects.filter(pk=pk).first()
<<<<<<< HEAD
=======

>>>>>>> 6b0291b086b7f6066fde113c91a1ee3af7a5133b
        final_score = selected_game.result_set

        if final_score.first() == final_score.last():

            if selected_game:
                return render(
                    request,
                    template_name=self.template_name,
                    context={"game": selected_game, "result": final_score},
                )
                raise Http404

        else:
            # mandar notify ao admin
            return HttpResponse("Aguardar resposta do tournament manager")
