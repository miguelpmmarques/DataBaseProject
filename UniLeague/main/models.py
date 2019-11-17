from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models.functions import Extract

from UniLeague.settings import MEDIA_URL

"""
DATA BASE MODELS CRIATION
"""


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


class Day(models.Model):
    day = models.DateField(null=True)

    class Meta:
        db_table = "Day"
        verbose_name = "Dia"
        verbose_name_plural = "Dias"
        ordering = ["-day"]

    def __str__(self):
        return str(self.day)


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



    # missing games and goals

    class Meta:
        db_table = "CustomUser"
        verbose_name = "Utilizador"
        verbose_name_plural = "Utilizadores"
        ordering = ["-username"]

    def __str__(self):
        return self.username


# foreign keys done, I think
class Position(models.Model):
    name = models.CharField(max_length=512, unique=True, null=False, default="")
    start = models.BooleanField()
    users = models.ManyToManyField(CustomUser)

    class Meta:
        db_table = "Position"
        verbose_name = "Posicao"
        verbose_name_plural = "Posicoes"
        ordering = ["-name"]

    def __str__(self):
        return self.name


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

class TimeSlot(models.Model):
    """
    weekDay = models.CharField(max_length=512, null=False, default="")
    Hour = models.IntegerField(null=False, default=0)
    Minute = models.IntegerField(null=False, default=0)
    """

    title = models.CharField(max_length=200, default="")
    description = models.TextField(null=True)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(auto_now=True)

    cost = models.IntegerField(null=False, default=0)
    isFree = models.BooleanField(null=False, default=True)
    field = models.ForeignKey(Field, null=False, on_delete=models.PROTECT)
    tournament = models.ForeignKey(Tournament, null=True, on_delete=models.PROTECT)

    class Meta:
        db_table = "TimeSlot"
        verbose_name = "Intervalo de tempo"
        verbose_name_plural = "Intervalos de tempo"

        ordering = ["-start_time"]

    def __str__(self):
        return str(self.start_time)


# foreign keys done i think
class Game(models.Model):
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
        return str(self.gameDate) + "Cost - " + str(self.cost)


class Result(models.Model):
    home_score = models.IntegerField(null=False, default=0)
    away_score = models.IntegerField(null=False, default=0)
    home_team = models.CharField(max_length=512, null=False, default="")
    away_team = models.CharField(max_length=512, null=False, default="")
    game = models.ForeignKey(Game, null=True, on_delete=models.PROTECT)
    player_scores = models.ManyToManyField(CustomUser)

    class Meta:
        db_table = "Result"
        verbose_name = "Resultado"
        verbose_name_plural = "Resultados"
        ordering = ["-home_score"]

    def __str__(self):
        return str(self.home_score) + " - " + str(self.away_score)


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
    players = models.ManyToManyField(CustomUser, blank=True, related_name="players")
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
