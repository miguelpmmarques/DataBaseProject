from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


class CustomUser(AbstractUser):

    cc = models.BigIntegerField(primary_key=True, null=False, blank=False)
    first_name = models.CharField(max_length=512, unique=True, null=False, blank=False)
    last_name = models.CharField(max_length=512, unique=True, null=False, blank=False)
    phone = PhoneNumberField(null=True, blank=True, unique=True, region="PT")
    budget = models.BigIntegerField(null=False)
    hierarchy = models.IntegerField(null=False)
    image = models.FileField(upload_to="users/%Y/%m/%d/", null=True, blank=True)
    # position = models.ManyToManyField(position, on_delete=models.PROTECT)

    class Meta:
        db_table = "CustomUser"
        verbose_name = "Utilizador"
        verbose_name_plural = "Utilizadores"
        ordering = ["-username"]

    def __str__(self):
        return self.username


class Tactic(models.Model):
    id = models.BigIntegerField(primary_key=True, null=False, blank=False)
    nrStrikers = models.IntegerField(null=False, blank=False)
    nrForwards = models.IntegerField(null=False, blank=False)
    nrMidfielders = models.IntegerField(null=False, blank=False)
    nrDefenders = models.IntegerField(null=False, blank=False)
    nrGoalies = models.IntegerField(null=False, blank=False)

    class Meta:
        db_table = "Tactic"
        verbose_name = "Tatica"

    def __str__(self):
        return str(self.id)


class Position(models.Model):
    name = models.CharField(max_length=512, unique=True, null=False)
    start = models.BooleanField()

    class Meta:
        db_table = "Position"
        verbose_name = "Posicao"
        verbose_name_plural = "Posicoes"
        ordering = ["-name"]

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=512, null=False)
    numberPlayers = models.IntegerField(null=False)

    class Meta:
        db_table = "Team"
        verbose_name = "Equipa"
        verbose_name_plural = "Equipas"
        ordering = ["-name"]

    def __str__(self):
        return self.name
