from django.urls import path
from django.urls import include

from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view()),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("users/validate/<int:pk>/", views.validate, name="validate"),
    path("users/", include("django.contrib.auth.urls")),
    path("users/rest/<int:pk>", views.RestUsers.as_view()),
]
