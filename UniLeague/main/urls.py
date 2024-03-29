from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = "main"

"""seeUserProfile, Miguelito, não faças isto pelo nome, manda o id do user. N tou a perceber mto bem se esta view é só para
o user que está logado, ou para o admin aceder a um user em particular. Se for para o user ver só o seu perfil
não é preciso fazer nenhum get, fazes só request.user
"""
urlpatterns = [
    path("administration/", views.AdminMenuView.as_view(), name="admin-menu"),
    path("help/", views.HelpView.as_view(), name="help-page"),
    path("", views.LandingPageView.as_view(), name="landing-page"),
    path("logout/", views.log_out_request, name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("notifications/", views.NotificationsView.as_view(), name="notification"),
    path("replaceReserve/", views.replaceSubseserve.as_view(), name="replaceReserve"),
    path("notifications/rest/<int:pk>/", views.NotificationsRestView.as_view()),
    path("notifyteam/<int:teampk>/", views.notifyTeam.as_view(), name="notification"),
    path(
        "replaceMember/<int:teampk>/",
        views.replaceMember.as_view(),
        name="notification",
    ),
    path("login/", views.LoginView.as_view(), name="login-view"),
    path("addReserve/<int:tournamentpk>/", views.addReserve.as_view()),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("users/validate/<int:pk>/", views.validate, name="validate"),
    path("users/validate/", views.validateMultiple, name="validate_multiple"),
    path(
        "users/goToTeam/", views.GoToTeamFromPlayer.as_view(), name="validate_multiple"
    ),
    path(
        "users/rest/captains/<int:tournamentId>/<int:pk>/",
        views.RestCaptainsList.as_view(),
    ),
    path("users/profile/<int:pk>/", views.ProfileView.as_view(), name="profile"),
    path("users/rest/<int:pk>/", views.RestUsers.as_view()),
    path("users/", include("django.contrib.auth.urls")),
    path("users/rest/list/patch/", views.RestUsersListPatch.as_view()),
    path("users/rest/list/", views.RestUsersList.as_view()),
    path(
        "team/apply/<int:pk>/",
        views.ChoosePositionView.as_view(),
        name="choosePosition",
    ),
    path(
        "tournaments/list/",
        views.CreateTournamentListView.as_view(),
        name="createTournament",
    ),
    path(
        "tournaments/create/",
        views.CreateTournamentView.as_view(),
        name="createTournament",
    ),
    path("tournaments/rest/list/", views.RestListTournaments.as_view()),
    path(
        "tournaments/<int:pk>/",
        views.TournamentDetailsView.as_view(),
        name="tournament-details",
    ),
    path("games/<int:pk>/", views.GameView.as_view()),
    path("positionchange/<int:playerpk>/<int:teampk>/", views.changePos.as_view()),
    path("updateTeamUserInfo/<int:playerpk>/<int:teampk>/", views.changeInfo.as_view()),
    path("teams/create/", views.CreateTeam.as_view(), name="createTeam"),
    path("teams/list/", views.CreateTeamView.as_view(), name="listTeam"),
    path("teams/profile/<int:pk>/", views.TeamView.as_view(), name="TeamProfile"),
    path("teams/rest/<int:pk>/", views.RestTeams.as_view()),
    path("teams/rest/list/", views.RestTeamsList.as_view()),
    path(
        "games/calendar/<str:filter>/<int:pk>/",
        views.CalendarView.as_view(),
        name="main-calendar",
    ),
    path("games/week/<int:pk>/", views.WeekCalendarView.as_view()),
    path("teamusers/rest/<int:pk>/", views.RestTeamUserView.as_view()),
    path(
        "games/generate/<int:tournament_pk>/",
        views.CreateGames.as_view(),
        name="generate-games",
    ),
    path("results/<int:pk>/", views.RestResults.as_view()),
    path("goals/<int:pk>/", views.RestGoals.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# path("teams/<int:pk>/", views.),
