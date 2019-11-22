from django.contrib import admin

from .models import CustomUser
from .models import Position
from .models import Field
from .models import Result
from .models import Tournament
from .models import Team
from .models import Tactic
from .models import TimeSlot
from .models import Game
from .models import GameWeekDay
from .models import Day
from .models import TeamUser
from .models import Notifications


# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    fields = [
        "username",
        "password",
        "first_name",
        "last_name",
        "citizen_card",
        "email",
        "phone",
        "hierarchy",
        "image",
        "isConfirmed",
        "isTournamentManager",
        "is_superuser",
        "is_active",
        "is_staff",
    ]


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Position)
admin.site.register(Field)
admin.site.register(Result)
admin.site.register(Tournament)
admin.site.register(Team)
admin.site.register(Tactic)
admin.site.register(TimeSlot)
admin.site.register(Game)
admin.site.register(GameWeekDay)
admin.site.register(Day)
admin.site.register(TeamUser)
admin.site.register(Notifications)
