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


class Game(models.Model):
    thisTime = models.TimeField(null=False)
    cost = models.IntegerField(null=False)
    gameDate = models.DateTimeField(null=False)

    class Meta:
        db_table = "Game"
        verbose_name = "Jogo"
        verbose_name_plural = "Jogos"
        ordering = ["-gameDate"]

    def __str__(self):
        return str(self.gameDate) + "Cost - " + self.cost


class Result(models.Model):
    home_score = models.IntegerField(null=False)
    away_score = models.IntegerField(null=False)

    class Meta:
        db_table = "Result"
        verbose_name = "Resultado"
        verbose_name_plural = "Resultados"
        ordering = ["-home_score"]

    def __str__(self):
        return str(self.home_score) + " - " + str(self.away_score)


class Field(models.Model):
    name = models.IntegerField(null=False)

    class Meta:
        db_table = "Field"
        verbose_name = "Campo"
        verbose_name_plural = "Campos"
        ordering = ["-name"]

    def __str__(self):
        return self.name


class TimeSlot(models.Model):
    weekDay = models.CharField(max_length=512, null=False)
    Hour = models.IntegerField(null=False)
    Minute = models.IntegerField(null=False)
    cost = models.IntegerField(null=False)
    isFree = models.BooleanField(null=False)

    class Meta:
        db_table = "TimeSlot"
        verbose_name = "Intervalo de tempo"
        verbose_name_plural = "Intervalos de tempo"
        ordering = ["-weekDay"]

    def __str__(self):
        return self.weekDay


class Tournament(models.Model):
    name = models.CharField(max_length=512, null=False, unique=True)
    beginTournament = models.DateTimeField(null=False)
    endTournament = models.DateTimeField(null=False)

    class Meta:
        db_table = "Tournament"
        verbose_name = "Torneio"
        verbose_name_plural = "Torneio"
        ordering = ["-name"]

    def __str__(self):
        return self.name
