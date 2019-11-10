from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.functions import Extract


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
    image = models.ImageField(upload_to="users/%Y/%m/%d/", null=True, blank=True)
    # Connection between Entities
    position = models.ManyToManyField(Position)
    # um utlizador pode estar inscrito em varias equipas desde
    # que n sejam do mesmo torneio, certo? senao fica foreign key
    result_scores = models.ManyToManyField(Result)

    class Meta:
        db_table = "CustomUser"
        verbose_name = "Utilizador"
        verbose_name_plural = "Utilizadores"
        ordering = ["-username"]

    def __str__(self):
        return self.username


class GameWeekDay(models.Model):
    DAYS_OF_WEEK = (
        ("0", "Monday"),
        ("1", "Tuesday"),
        ("2", "Wednesday"),
        ("3", "Thursday"),
        ("4", "Friday"),
        ("5", "Saturday"),
        ("6", "Sunday"),
    )

    week_day = models.CharField(
        max_length=2, choices=DAYS_OF_WEEK, null=False, default=0
    )

    class Meta:
        db_table = "WeekDay"
        verbose_name = "Dia de Semana"
        verbose_name_plural = "Dias de Semana"
        ordering = ["-week_day"]

    def get_week_day(self):
        return str(self.DAYS_OF_WEEK[int(self.week_day)][1])

    def __str__(self):
        return self.get_week_day()


class Day(models.Model):
    day = models.DateField(null=True)

    class Meta:
        db_table = "Day"
        verbose_name = "Dia"
        verbose_name_plural = "Dias"
        ordering = ["-day"]

    def __str__(self):
        return str(self.day)


class Tournament(models.Model):
    name = models.CharField(max_length=512, null=False, unique=True, default="")
    beginTournament = models.DateTimeField(null=True)
    endTournament = models.DateTimeField(null=True)
    number_of_hands = models.IntegerField(default=0)
    number_teams = models.IntegerField(default=0, null=False)
    # TALVEZ DEVA SER 1 to 1
    tournament_manager = models.ForeignKey(
        CustomUser, null=False, on_delete=models.PROTECT
    )
    fields = models.ManyToManyField(Field)
    game_week_days = models.ManyToManyField(GameWeekDay)
    days_without_games = models.ManyToManyField(Day)
    tournament_badge = models.ImageField(
        upload_to="users/%Y/%m/%d/", blank=True, null=True
    )

    class Meta:
        db_table = "Tournament"
        verbose_name = "Torneio"
        verbose_name_plural = "Torneio"
        ordering = ["-name"]

    def __str__(self):
        return self.name


# foreign keys done
class Team(models.Model):
    name = models.CharField(max_length=512, null=False, default="")
    numberPlayers = models.IntegerField(null=False, default=1)
    tournament = models.ForeignKey(Tournament, null=True, on_delete=models.PROTECT)
    players = models.ManyToManyField(CustomUser)
    teamLogo = models.FileField(upload_to="users/%Y/%m/%d/", null=True, blank=True)

    class Meta:
        db_table = "Team"
        verbose_name = "Equipa"
        verbose_name_plural = "Equipas"
        ordering = ["-name"]

    def __str__(self):
        return self.name


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
        return str(self.pk)


class TimeSlot(models.Model):
    """
    weekDay = models.CharField(max_length=512, null=False, default="")
    Hour = models.IntegerField(null=False, default=0)
    Minute = models.IntegerField(null=False, default=0)
    """

    date_time = models.DateTimeField(null=True)
    cost = models.IntegerField(null=False, default=0)
    isFree = models.BooleanField(null=False, default=True)
    field = models.ForeignKey(Field, null=False, on_delete=models.PROTECT)
    tournament = models.ForeignKey(Tournament, null=True, on_delete=models.PROTECT)

    class Meta:
        db_table = "TimeSlot"
        verbose_name = "Intervalo de tempo"
        verbose_name_plural = "Intervalos de tempo"
        ordering = ["-date_time"]

    def __str__(self):
        return self.weekDay


# foreign keys done i think
class Game(models.Model):
    thisTime = models.TimeField(null=False, auto_now_add=True)
    cost = models.IntegerField(null=False, default=0)
    gameDate = models.OneToOneField(Day, on_delete=models.PROTECT)
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
