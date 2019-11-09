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

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(Position)
admin.site.register(Field)
admin.site.register(Result)
admin.site.register(Tournament)
admin.site.register(Team)
admin.site.register(Tactic)
admin.site.register(TimeSlot)
admin.site.register(Game)
