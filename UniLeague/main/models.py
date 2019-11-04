from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField


"""
DATA BASE MODELS CRIATION
"""

# foreign keys done i think
class CustomUser(AbstractUser):

    # Privilegies
    isCaptain = models.BooleanField(null=False)
    isTournamentManager = models.BooleanField(null=False)
    isAdmin = models.BooleanField(null=False)
    # Atributes
    cc = models.BigIntegerField(primary_key=True, null=False, blank=False)
    first_name = models.CharField(max_length=512, unique=True, null=False, blank=False)
    last_name = models.CharField(max_length=512, unique=True, null=False, blank=False)
    phone = PhoneNumberField(null=True, blank=True, unique=True, region="PT")
    budget = models.BigIntegerField(null=False)
    hierarchy = models.IntegerField(null=False)
    image = models.FileField(upload_to="users/%Y/%m/%d/", null=True, blank=True)
    # Connection between Entities
    position = models.ManyToManyField(Position, on_delete=models.PROTECT)
    # um utlizador pode estar inscrito em varias equipas desde que n sejam do mesmo torneio, certo? senao fica foreign key
    team = models.ManyToManyField(Team, on_delete=models.PROTECT)
    result_scores = models.ManyToManyField(Result, on_delete=Models.PROTECT)

    class Meta:
        db_table = "CustomUser"
        verbose_name = "Utilizador"
        verbose_name_plural = "Utilizadores"
        ordering = ["-username"]

    def __str__(self):
        return self.username


# foreign keys done
class Tactic(models.Model):
    # Atributes
    # found better way to do dis
    """
    id = models.BigIntegerField(primary_key=True, null=False, blank=False)
    nrStrikers = models.IntegerField(null=False, blank=False)
    nrForwards = models.IntegerField(null=False, blank=False)
    nrMidfielders = models.IntegerField(null=False, blank=False)
    nrDefenders = models.IntegerField(null=False, blank=False)
    nrGoalies = models.IntegerField(null=False, blank=False)
    """
    # Connection between Entities
    positions = models.ManyToManyField(Position)
    team = models.ManyToManyField(Team)

    class Meta:
        db_table = "Tactic"
        verbose_name = "Tatica"

    def __str__(self):
        return str(self.id)


# foreign keys done, I think
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


# foreign keys done
class Team(models.Model):
    name = models.CharField(max_length=512, null=False)
    numberPlayers = models.IntegerField(null=False)
    captain = models.OneToOneField(CustomUser, null=False)
    tournament = models.ForeignKey(Tournament, null=True)

    class Meta:
        db_table = "Team"
        verbose_name = "Equipa"
        verbose_name_plural = "Equipas"
        ordering = ["-name"]

    def __str__(self):
        return self.name


# foreign keys done i think
class Game(models.Model):
    thisTime = models.TimeField(null=False)
    cost = models.IntegerField(null=False)
    gameDate = models.DateTimeField(null=False)
    team_1 = models.ForeignKey(Team, null=False)
    team_2 = models.ForeignKey(Team, null=False)
    score_1 = models.ForeignKey(Result, null=True)
    score_2 = models.ForeignKey(Result, null=True)
    tournament = models.ForeignKey(Tournament, null=False)
    # timeslot not sure if ok
    timeslot = models.OneToOneField(TimeSlot, null=False)
    field = models.ForeignKey(Field, null=False)

    class Meta:
        db_table = "Game"
        verbose_name = "Jogo"
        verbose_name_plural = "Jogos"
        ordering = ["-gameDate"]

    def __str__(self):
        return str(self.gameDate) + "Cost - " + self.cost


# foreign keys done i think
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
    field = models.ForeignKey(Field, null=False)
    tournament = models.ForeignKey(Tournament, null=True)

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
    tournament_manager = models.ForeignKey(CustomUser, null=False)
    fields = models.ManyToManyField(Field, null=False)

    class Meta:
        db_table = "Tournament"
        verbose_name = "Torneio"
        verbose_name_plural = "Torneio"
        ordering = ["-name"]

    def __str__(self):
        return self.name
