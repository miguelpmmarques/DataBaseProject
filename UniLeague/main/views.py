from django.shortcuts import render
from django.views.generic import View

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from django.urls import reverse_lazy
from django.views import generic
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import Http404
from django.http import HttpResponseBadRequest
from django.http import HttpResponseRedirect
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.db import transaction
from django.db import IntegrityError
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
from .tokens import account_activation_token
from .tasks import ask_admin_for_permissions
from .forms import CustomUserForm

# from .forms import CustomUserLoginForm
from .models import CustomUser

from time import sleep


class LandingPageView(generic.TemplateView):
    template_name = "main/MainMenu.html"


# Create your views here.
class LoginView(generic.CreateView):
    template_name = "main/login.html"
    form_class = AuthenticationForm

    def get(self, request):
        return render(
            request, template_name=self.template_name, context={"form": self.form_class}
        )

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
            return HttpResponseBadRequest


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
        print(serializer.data)
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


class RestUsersList(APIView):
    allowed_methods = "PATCH"
    # authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAdminUser]

    def patch(self, request):
        data = request.data
        print(data)
        try:
            for elem in request.data:
                print("ELEM===", elem)
                instance = CustomUser.objects.get(pk=list(elem.keys())[0])
                print("instance==", instance)
                serializer = CustomUserSerializer(
                    instance, data=list(elem.values())[0], partial=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
            return Response("success")
        except Exception as exp:
            print("exp::", exp)
            raise exp
