from django.urls import path
from django.urls import include

from . import views

urlpatterns = [path("register/", views.RegisterView.as_view())]
