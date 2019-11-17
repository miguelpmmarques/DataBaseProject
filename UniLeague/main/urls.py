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
    path("", views.LandingPageView.as_view(), name="landing-page"),
    path("logout/", views.log_out_request, name="logout"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("users/validate/<int:pk>/", views.validate, name="validate"),
    path("users/validate/", views.validateMultiple, name="validate_multiple"),
    path(
        "users/rest/captains/<int:tournamentId>/<int:pk>/",
        views.RestCaptainsList.as_view(),
    ),
    path("users/profile/<int:pk>/", views.ProfileView.as_view(), name="profile"),
    path("users/rest/<int:pk>", views.RestUsers.as_view()),
    path("users/", include("django.contrib.auth.urls")),
    path("users/rest/list/patch/", views.RestUsersListPatch.as_view()),
    path("users/rest/list/", views.RestUsersList.as_view()),
    path(
        "team/apply/<str:team_selected>",
        views.ChoosePositionView.as_view(),
        name="choosePosition",
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
    path("teams/create/", views.CreateTeam.as_view(), name="createTeam"),
    path("teams/profile/<str:param>/", views.TeamView.as_view(), name="TeamProfile"),
    path("teams/rest/<int:pk>/", views.RestTeams.as_view()),
    path("teams/rest/list/", views.RestTeamsList.as_view()),
    path("games/calendar/<year>/", views.CalendarView.as_view(), name="main-calendar"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# path("teams/<int:pk>/", views.),
