from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import TimeSlot


class Calendar(HTMLCalendar):
    def __init__(self, year=None, month=None):
        self.year = year
        self.month = month
        super(Calendar, self).__init__()

    # formats a day as a td
    # filter events by day
    def formatday(self, day, events):
        events_per_day = events.filter(start_time__day=day)
        print("events per day", events_per_day)
        d = ""
        for event in events_per_day:
            d += f"<li id='{event.pk}' name='{event.game}'><span class='badge badge-pill badge-secondary'><a href='/games/{event.game.pk}' style='color:white'> {event.title} </a></span></li>"

        if day != 0:
            return f"<td class='border border-secondary'><span class='date'>{day}</span><ul> {d} </ul></td>"
        return "<td></td>"

    # formats a week as a tr
    def formatweek(self, theweek, events):
        week = ""
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f"<tr class='border border-secondary'> {week} </tr>"

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
        events = TimeSlot.objects.filter(
            start_time__year=self.year, start_time__month=self.month, isFree=False
        )

        cal = f'<table border="1" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f"{self.formatmonthname(self.year, self.month, withyear=withyear)}\n"
        cal += f"{self.formatweekheader()}\n"
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f"{self.formatweek(week, events)}\n"
        return cal
