from datetime import timedelta

from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text
from django.utils import timezone
from django.db import transaction
from django.db import IntegrityError


from UniLeague.celery import app
from celery.schedules import crontab

from .models import CustomUser
from .models import Notifications
from .models import TimeSlot
from .models import Tournament
from .models import TeamUser
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
            {"admin": admin, "user": user, "domain": host + "/users/validate"},
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
                print("ELEM===", elem)
                elem.is_active = False
                elem.save()
    except IntegrityError:
        raise self.retry()


@app.task(
    name="send_notification_for_absences",
    bind=True,
    ignore_result=False,
    task_retries=5,
    default_retry_delay=60,
)
def send_notification_for_absences(self):
    print("oi atão!")
    try:
        with transaction.atomic():
            absentees = TeamUser.objects.filter(absences__gte=5)
            for elem in absentees:
                print(elem)
                notification = Notifications.objects.filter(
                    title="The user "
                    + elem.player.username
                    + " has "
                    + str(elem.absences)
                    + " absences"
                ).first()
                if not notification:
                    notification = Notifications.objects.create(
                        title="The user "
                        + elem.player.username
                        + " has "
                        + str(elem.absences)
                        + " absences",
                        description="<br> Please go to your administration menu if you want to blacklist him/her.",
                        user_send=CustomUser.objects.get(is_superuser=True),
                        origin="System",
                    ).save()
                print(notification)

    except IntegrityError:
        raise self.retry()


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
            absentees = TeamUser.objects.filter(absences__gte=5)
            for elem in absentees:
                print(elem)
                notification = Notifications.objects.filter(
                    title="The user "
                    + elem.player.username
                    + " has "
                    + str(elem.absences)
                    + " absences"
                ).first()
                if not notification:
                    notification = Notifications.objects.create(
                        title="The user "
                        + elem.player.username
                        + " has "
                        + str(elem.absences)
                        + " absences",
                        description="<br> Please go to your administration menu if you want to blacklist him/her.",
                        user_send=CustomUser.objects.get(is_superuser=True),
                        origin="System",
                    ).save()
                print(notification)

    except IntegrityError:
        raise self.retry()
