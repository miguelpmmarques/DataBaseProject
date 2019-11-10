from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


"""
DATA BASE MODELS CRIATION
"""


# foreign keys done, I think
class Position(models.Model):
    name = models.CharField(max_length=512, unique=True, null=False, default="")
    start = models.BooleanField()

    class Meta:
        db_table = "Position"
        verbose_name = "Posicao"
        verbose_name_plural = "Posicoes"
        ordering = ["-name"]

    def __str__(self):
        return self.name


class Field(models.Model):
    name = models.CharField(max_length=512, null=False, default="")

    class Meta:
        db_table = "Field"
        verbose_name = "Campo"
        verbose_name_plural = "Campos"
        ordering = ["-name"]

    def __str__(self):
        return self.name


# foreign keys done i think
class Result(models.Model):
    home_score = models.IntegerField(null=False, default=0)
    away_score = models.IntegerField(null=False, default=0)
    home_team = models.CharField(max_length=512, null=False, default="")
    away_team = models.CharField(max_length=512, null=False, default="")

    class Meta:
        db_table = "Result"
        verbose_name = "Resultado"
        verbose_name_plural = "Resultados"
        ordering = ["-home_score"]

    def __str__(self):
        return str(self.home_score) + " - " + str(self.away_score)


class CustomUser(AbstractUser):
    # has confirmed by email
    isConfirmed = models.BooleanField(null=False, default=True)
    # Privilegies
    email = models.EmailField(unique=True)
    isCaptain = models.BooleanField(null=False, default=False)
    isTournamentManager = models.BooleanField(null=False, default=False)
    # is_superuser(admin) is already
    # Atributes
    citizen_card = models.BigIntegerField(null=False, default=0, blank=False)
    first_name = models.CharField(max_length=512, unique=False, null=True, blank=False)
    last_name = models.CharField(max_length=512, unique=False, null=True, blank=False)
    phone = PhoneNumberField(null=False, blank=True, unique=False, region="PT")
    budget = models.BigIntegerField(null=False, default=0)
    hierarchy = models.IntegerField(null=False, default=0)
    image = models.FileField(upload_to="users/%Y/%m/%d/", null=True, blank=True)
    # Connection between Entities
    position = models.ManyToManyField(Position)
    # um utlizador pode estar inscrito em varias equipas desde que n sejam do mesmo torneio, certo? senao fica foreign key
    result_scores = models.ManyToManyField(Result)

    class Meta:
        db_table = "CustomUser"
        verbose_name = "Utilizador"
        verbose_name_plural = "Utilizadores"
        ordering = ["-username"]

    def __str__(self):
        return self.username


class Tournament(models.Model):
    name = models.CharField(max_length=512, null=False, unique=True, default="")
    beginTournament = models.DateTimeField(null=False, auto_now_add=True)
    endTournament = models.DateTimeField(null=False, auto_now_add=True)
    number_teams = models.IntegerField(default=0, null=False)
    # TALVEZ DEVA SER 1 to 1
    tournament_manager = models.OneToOneField(
        CustomUser, null=False, on_delete=models.PROTECT,
    )
    fields = models.ManyToManyField(Field)

    class Meta:
        db_table = "Tournament"
        verbose_name = "Torneio"
        verbose_name_plural = "Torneio"
        ordering = ["-name"]

    def __str__(self):
        return self.name


# foreign keys done
class Tactic(models.Model):
    # Atributes
    positions = models.ManyToManyField(Position)
    name = models.CharField(max_length=20, default="tatica")

    class Meta:
        db_table = "Tactic"
        verbose_name = "Tatica"

    def __str__(self):
        return self.name


# foreign keys done
class Team(models.Model):
    name = models.CharField(max_length=512, null=False, default="")
    numberPlayers = models.IntegerField(null=True, default=1)
    tournament = models.ForeignKey(Tournament, null=True, on_delete=models.PROTECT)
    players = models.ManyToManyField(
        CustomUser, blank=True, null=True, related_name="players",
    )
    captain = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    tactic = models.ForeignKey(Tactic, null=True, on_delete=models.PROTECT)
    teamLogo = models.ImageField(
        upload_to="images/", null=True, verbose_name="teamLogo", blank=True
    )

    class Meta:
        db_table = "Team"
        verbose_name = "Equipa"
        verbose_name_plural = "Equipas"
        ordering = ["-name"]

    def __str__(self):
        return self.name + str(self.teamLogo)


class TimeSlot(models.Model):
    weekDay = models.CharField(max_length=512, null=False, default="")
    Hour = models.IntegerField(null=False, default=0)
    Minute = models.IntegerField(null=False, default=0)
    cost = models.IntegerField(null=False, default=0)
    isFree = models.BooleanField(null=False, default=True)
    field = models.ForeignKey(Field, null=False, on_delete=models.PROTECT)
    tournament = models.ForeignKey(Tournament, null=True, on_delete=models.PROTECT)

    class Meta:
        db_table = "TimeSlot"
        verbose_name = "Intervalo de tempo"
        verbose_name_plural = "Intervalos de tempo"
        ordering = ["-weekDay"]

    def __str__(self):
        return self.weekDay


# foreign keys done i think
class Game(models.Model):
    thisTime = models.TimeField(null=False, auto_now_add=True)
    cost = models.IntegerField(null=False, default=0)
    gameDate = models.DateTimeField(null=False, auto_now_add=True)
    score = models.ForeignKey(Result, null=True, on_delete=models.PROTECT)
    tournament = models.ForeignKey(Tournament, null=False, on_delete=models.PROTECT)
    # timeslot not sure if ok
    timeslot = models.OneToOneField(TimeSlot, null=False, on_delete=models.PROTECT)
    field = models.ForeignKey(Field, null=True, on_delete=models.PROTECT)

    class Meta:
        db_table = "Game"
        verbose_name = "Jogo"
        verbose_name_plural = "Jogos"
        ordering = ["-gameDate"]

    def __str__(self):
        return str(self.gameDate) + "Cost - " + self.cost
