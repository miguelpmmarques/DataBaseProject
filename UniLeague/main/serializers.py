from UniLeague.settings import DATE_INPUT_FORMATS

from rest_framework import serializers

from .models import CustomUser
from .models import GameWeekDay
from .models import Tournament
from .models import Field
from .models import Team
from .models import Position
from .models import TeamUser
from .models import Goal
from .models import TimeSlot
from .models import Game


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"


class PartialCustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "date_joined",
            "citizen_card",
            "phone",
        )


class DaySerializer(serializers.Serializer):
    day = serializers.DateField(format="%d%m%Y")


class TournamentSerializer(serializers.ModelSerializer):
    days_without_games = DaySerializer(many=True, required=False)

    class Meta:
        model = Tournament
        fields = "__all__"


class TeamUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamUser
        fields = "__all__"


class TeamSerializer(serializers.ModelSerializer):
    teamuser_set = TeamUserSerializer(many=True, required=False)

    class Meta:
        model = Team
        fields = "__all__"


class TeamSerializerCreate(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = "__all__"


class DaySerializer(serializers.Serializer):
    day = serializers.DateField(format="%d%m%Y")


class GameWeekDaySerializer(serializers.Serializer):
    week_day = serializers.CharField(source="get_week_day")


class FieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = Field
        fields = "__all__"


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        fields = ("time", "scorer")


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = "__all__"


class TimeSlotSerializer(serializers.ModelSerializer):
    game = GameSerializer(required=False)

    class Meta:
        model = TimeSlot
        fields = "__all__"
