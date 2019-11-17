import json

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
from .models import Position

from time import sleep


# Create your views here.


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
        return HttpResponseRedirect(reverse("landing-page"))

    def post(self, request):
        """
        overriding native post method, for e-mail sending with token verification
        """
        user = request.user
        if user.is_authenticated:
            form = TeamCreationForm(request.POST)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        team = form.save(commit=False)
                        team.captain = user
                        user.isCaptain = True
                        user.save()
                        team.save()
                        team.players.add(user)
                except IntegrityError as err:
                    print("Database Integrity error:", err)
                    return HttpResponse(
                        "Critical database error\nUnable to save your user\nPlease try again"
                    )
                return HttpResponseRedirect("/team/apply/" + team.name)
            return HttpResponse("Please Fill all Fields")
        return HttpResponseRedirect(reverse("landing-page"))


class TeamView(generic.DetailView):
    template_name = "main/profileTeam.html"

    def get(self, request):
        if request.user.is_authenticated:
            team_selected = Team.objects.get(captain=request.user.pk)
            return render(
                request,
                template_name=self.template_name,
                context={"myTeam": team_selected, "players": team_selected.players},
            )
        return HttpResponseRedirect(reverse("landing-page"))


class ChoosePositionView(generics.RetrieveUpdateAPIView):
    template_name = "main/teamApply.html"
    allowed_methods = "PATCH"

    def get(self, request, team_selected):

        team = Team.objects.get(name=team_selected)
        tactic = team.tactic

        return render(
            request,
            template_name=self.template_name,
            context={"team": team, "tactic": tactic},
        )

    def patch(self, request, team_selected):
        team = Team.objects.get(name=team_selected)

        try:
            position = team.tactic.positions.get(name=request.data["position"])
            position.users.add(request.user)
            position.save()
            # data_copy.update({"position": position.pk})
            # data_copy = CustomUserSerializer(request.user).data.copy()
            # new_pos = data_copy["position"]
            # CustomUserSerializer(request.user, {"position": new_pos}, partial=True)

        except Position.DoesNotExist:
            raise Http404
        print(request.data["position"])

        return Response("success")
        # return HttpResponseRedirect(reverse("landing-page"))


class TeamView(generic.DetailView):
    template_name = "main/profileTeam.html"

    def get(self, request):
        if request.user.is_authenticated:
            team_selected = Team.objects.get(captain=request.user.pk)
            return render(
                request,
                template_name=self.template_name,
                context={"myTeam": team_selected, "players": team_selected.players},
            )
        return HttpResponseRedirect(reverse("landing-page"))


def profileOtherView(request, user_selected):
    user = CustomUser.objects.get(username=user_selected)
    return render(request, template_name="main/profile.html", context={"user": user})


def profileTeamOtherView(request, team_selected):
    print("Chegou aqui")
    team = Team.objects.get(name=team_selected)
    return render(
        request, template_name="main/profileTeam.html", context={"myTeam": team}
    )


class ProfileView(generic.TemplateView):
    template_name = "main/profile.html"


class LandingPageView(generic.TemplateView):
    template_name = "main/MainMenu.html"

    def get(self, request):
        try:
            tournaments = TournamentSerializer(Tournament.objects.all(), many=True).data
            teams = TeamSerializer(Team.objects.all(), many=True).data
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
    return HttpResponseRedirect(reverse("landing-page"))


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
        return HttpResponseRedirect(reverse("landing-page"))

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
            return HttpResponseRedirect(data.get("next", "/"))
        else:
            raise Http404


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
            return HttpResponse(
                "Please confirm your email address to complete the registration"
            )
        print(form.errors)
        return HttpResponse("Please Fill all Fields")


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
            return HttpResponseRedirect(reverse("landing-page"))

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
            return HttpResponseRedirect(reverse("landing-page"))


class RestTournaments(generics.RetrieveUpdateAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = [IsAuthenticated]


class RestListTournaments(generics.ListAPIView):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer

    def list(self, request, *args, **kwarg):
        print("HERE")
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
            template_name="main/admin_validation_multiple.html",
            context={"users": serializer.data},
        )
    else:
        raise Http404


class RestUsers(generics.RetrieveUpdateAPIView):
    queryset = CustomUser.objects.all()
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
    queryset = CustomUser.objects.filter(isCaptain=True)

    def list(self, request, tournamentId):

        q_set = CustomUser.objects.filter(isCaptain=True).team_set(
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

    def list(self, request, *args, **kwargs):
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
