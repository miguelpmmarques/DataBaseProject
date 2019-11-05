from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text


from UniLeague.celery import app

from .models import CustomUser
from .tokens import account_activation_token


@app.task(
    name="ask_admin_for_permissions",
    bind=True,
    ignore_result=False,
    task_retries=5,
    default_retry_delay=60,
)
def ask_admin_for_permissions(self, host, pk):
    user = CustomUser.objects.get(pk=pk)
    mail_subject = "Activate your UniLeague account."
    admin = CustomUser.objects.filter(isAdmin=True).first()
    message = render_to_string(
        "main/activate_user.html",
        {"admin": admin, "user": user, "domain": host + "/users/validate"},
    )
    email = EmailMessage(mail_subject, message, to=[admin.email])
    email.send()
