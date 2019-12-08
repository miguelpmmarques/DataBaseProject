from datetime import timedelta

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.utils import timezone
from django.db import transaction
from django.db import IntegrityError
from django.db.models import F


from UniLeague.celery import app
from celery.schedules import crontab

from .models import CustomUser
from .models import Notifications
from .models import TimeSlot
from .models import Tournament
from .models import TeamUser
from .models import Team
from .models import Game
from .models import Result

from .tokens import account_activation_token


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        1, erase_timeslots.s(), name="erase useless timeslots every day"
    )


app.conf.beat_schedule = {
    # Executes every Monday morning at 7:30 a.m.
    "erase_timeslots": {
        "task": "erase_timeslots",
        "schedule": crontab(hour=0, minute=0),
        "args": (),
    },
    "deactivate_ended_tournaments": {
        "task": "deactivate_ended_tournaments",
        "schedule": crontab(hour=0, minute=0),
        "args": (),
    },
    "send_notification_for_absences": {
        "task": "send_notification_for_absences",
        "schedule": crontab(hour=0, minute=0),
        "args": (),
    },
    "verify_hierarchy": {
        "task": "verify_hierarchy",
        "schedule": crontab(hour=0, minute=0),
        "args": (),
    },
    "check_games_results": {
        "task": "check_games_results",
        "schedule": crontab(hour=0, minute=0),
        "args": (),
    },
    "check_for_negative_budget": {
        "task": "check_for_negative_budget",
        "schedule": crontab(hour=0, minute=0),
        "args": (),
    },
}


@app.task(
    name="ask_admin_for_permissions",
    bind=True,
    ignore_result=False,
    task_retries=5,
    default_retry_delay=60,
)
def ask_admin_for_permissions(self, host, pk):
    try:
        user = CustomUser.objects.get(pk=pk)
        mail_subject = "Activate your UniLeague account."
        admin = CustomUser.objects.filter(is_superuser=True).first()
        message = render_to_string(
            "main/email_activate_user.html",
            {"admin": admin, "user": user, "domain": host},
        )
        email = EmailMessage(mail_subject, message, to=[admin.email])
        return email.send()
    except CustomUser.DoesNotExist:
        return self.retry()


@app.task(
    name="erase_timeslots",
    bind=True,
    ignore_result=False,
    task_retries=5,
    default_retry_delay=60,
)
def erase_timeslots(self):
    try:
        with transaction.atomic():
            empty_timeslots = TimeSlot.objects.filter(description="")
            for empty_slot in empty_timeslots:
                print("TIEMSLUT====", empty_slot.description)
                empty_slot.delete()
    except IntegrityError:
        raise self.retry()
    return True


@app.task(
    name="deactivate_ended_tournaments",
    bind=True,
    ignore_result=False,
    task_retries=5,
    default_retry_delay=60,
)
def deactivate_ended_tournaments(self):
    try:
        with transaction.atomic():
            ended_tournaments = Tournament.objects.filter(
                endTournament__lte=timezone.now() - timedelta(days=5)
            )
            for elem in ended_tournaments:
                elem.is_active = False
                elem.save()
    except IntegrityError:
        raise self.retry()
    return True


@app.task(
    name="send_notification_for_absences",
    bind=True,
    ignore_result=False,
    task_retries=5,
    default_retry_delay=60,
)
def send_notification_for_absences(self):
    try:
        with transaction.atomic():
            absentees = TeamUser.objects.filter(absences__gte=5)
            for elem in absentees:
                notification = Notifications.objects.get_or_create(
                    title="The user "
                    + elem.player.username
                    + " has "
                    + str(elem.absences)
                    + " absences",
                    description="<br> <h3>This  user has been automatically removed from his team after this many strikes. Please go to your administration menu if you want to blacklist him/her.</h3>",
                    user_send=CustomUser.objects.get(is_superuser=True),
                    origin="System",
                ).save()

                notification = Notifications.objects.get_or_create(
                    title="The user "
                    + elem.player.username
                    + " has "
                    + str(elem.absences)
                    + " absences",
                    description="<br> <h3>This  user has been automatically removed from his team after this many strikes. Please contact your administrator for more information.</h3>",
                    user_send=elem.team.teamuser_set.filter(isCaptain=True).first(),
                    origin="System",
                ).save()
                elem.delete()

                notification = Notifications.objects.get_or_create(
                    title="You have " + str(elem.absences) + " absences",
                    description="<br> <h3>You have been automatically banned from the team"
                    + str(elem.team.name)
                    + ". Please contact your administrator for more information.</h3>",
                    user_send=elem,
                    origin="System",
                ).save()
                elem.delete()

            print(notification)
            absentees = TeamUser.objects.filter(absences__gte=3)
            for elem in absentees:
                notification = Notifications.objects.get_or_create(
                    title="You have " + str(elem.absences) + " absences",
                    description="<br> <h3>Two more and you will be banned from the team +"
                    + str(elem.team.name)
                    + ". Talk to your captain for more information.</h3>",
                    user_send=CustomUser.objects.get(is_superuser=True),
                    origin="System",
                ).save()

    except IntegrityError:
        raise self.retry()
    return True


@app.task(
    name="verify_hierarchy",
    bind=True,
    ignore_result=False,
    task_retries=5,
    default_retry_delay=60,
)
def verify_hierarchy(self):
    try:
        with transaction.atomic():
            for team in Team.objects.all():
                change_lineup_hierarchy_points("Avancado")
                change_lineup_hierarchy_points("Defesa")
                change_lineup_hierarchy_points("Medio")
                change_lineup_hierarchy_points("Striker")
                change_lineup_hierarchy_points(
                    "Guarda-Redes"
                )  # change starting defenders based on their hierarchy

    except IntegrityError:
        raise self.retry()
    return True


def change_lineup_hierarchy_points(parser):
    players = TeamUser.objects.filter(position__name__icontains=parser)
    count_starters = players.filter(position__start=True).count()
    ordered_players = players.order_by("-player__hierarchy")
    for i in range(players.count()):
        if i <= count_starters:
            ordered_players[i].position.start = True
        else:
            ordered_players[i].position.start = False


@app.task(
    name="check_games_results",
    bind=True,
    ignore_result=False,
    task_retries=5,
    default_retry_delay=60,
)
def check_games_results(self):
    today = timezone.now()
    try:
        with transaction.atomic():
            finished_games = Game.objects.filter(timeslot__start_time__lte=today)
            for game in finished_games:
                # updating user budgets
                game.teamusers_set.all().update(budget=F("budget") - game.cost)
                results = game.result_set.all()
                if not results.filter(is_final=True).exists():
                    first_result = results.first()
                    second_result = results.last()
                    if (
                        first_result
                        and second_result
                        and (first_result != second_result)
                    ):
                        results_equal = compareResults(first_result, second_result)
                        if results_equal:
                            first_result.is_final = True
                            first_result.save()
                        else:

                            tournament_manager = game.tournament.tournament_manager
                            try:
                                notification = Notifications.objects.get(
                                    title="The game "
                                    + game.timeslot.title
                                    + " has conflicts in the results set by both captains."
                                )
                            except Notifications.DoesNotExist:
                                home_captain = game.home_team.teamuser_set.filter(
                                    isCaptain=True
                                ).first()
                                notification = Notifications.objects.create(
                                    title="The game "
                                    + game.timeslot.title
                                    + " has conflicts in the results set by both captains.",
                                    description="<br> <h3>Please correct this error.<h3>",
                                    user_send=game.tournament.tournament_manager,
                                    origin="System",
                                    html='<button type="button" class="btn btn-dark" onclick=window.location.href="/games/'
                                    + str(game.pk)
                                    + '/">Verify Result</button>',
                                )
                                notification.save()
                                print(notification)
    except IntegrityError:
        raise self.retry()
    return True


def compareResults(f, s):
    if f and s and f != s:
        if f.home_score == f.home_score and f.away_score == f.away_score:
            goals_f = f.goal_set.all().order_by("-time")
            goals_s = s.goal_set.all().order_by("-time")
            count = 0
            if goals_f.count() == goals_s.count():
                for i in range(goals_f.count()):
                    if (
                        goals_f[i].scorer.pk == goals_s[i].scorer.pk
                        and goals_f[i].time == goals_s[i].time
                    ):
                        count += 1
            if count == goals_f.count():
                return True
        return False


@app.task(
    name="check_for_negative_budget",
    bind=True,
    ignore_result=False,
    task_retries=5,
    default_retry_delay=60,
)
def check_for_negative_budget(self):
    team_users = TeamUser.objects.filter(budget__lt=0)
    for team_user in team_users:
        try:
            with transaction.atomic():
                notification = Notifications.objects.get_or_create(
                    title="Your budget is bellow zero ",
                    description="<br> <h3>Your budget is"
                    + str(team_user.budget)
                    + "</h3><h3>Please pay your bills to your captain.</h3>",
                    user_send=team_user.player,
                    origin="System",
                    html="",
                )
                notification.save()
        except IntegrityError:
            raise self.retry()
        print(notification)
        return True
