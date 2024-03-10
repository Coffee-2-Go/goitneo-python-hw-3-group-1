from datetime import datetime, timedelta
from collections import defaultdict
import calendar


def get_birthdays_per_week(book, *_):
    upcoming_birthdays = defaultdict(list)
    today = datetime.today().date()
    for user in book.values():
        if user.birthday.value:
            birthday = user.birthday.value
            try:  # can be ValueError here if the birthday is on February 29
                next_birthday = birthday.replace(year=today.year)
            except ValueError:
                next_birthday = datetime(today.year, 3, 1)

            if next_birthday < today and next_birthday.month == 1:
                next_birthday = next_birthday.replace(year=today.year + 1)

            if next_birthday.weekday() == 5:
                next_birthday = next_birthday + timedelta(days=2)
            if next_birthday.weekday() == 6:
                next_birthday = next_birthday + timedelta(days=1)

            delta_days = (next_birthday - today).days

            if delta_days < 7:
                day_of_the_week = next_birthday.weekday()
                user_name = user.name.value
                upcoming_birthdays[day_of_the_week].append(user_name)

    if not upcoming_birthdays:
        return "No upcoming birthdays"
    
    sorted_result = dict(sorted(upcoming_birthdays.items()))

    day_today = today.weekday()

    birthdays_this_week = dict(
        filter(lambda week_day: week_day[0] >= day_today, sorted_result.items())
    )
    birthdays_next_week = dict(
        filter(lambda week_day: week_day[0] < day_today, sorted_result.items())
    )

    result = ""
    if birthdays_this_week:
        result += "This week:\n"
        for day, names in birthdays_this_week.items():
            result += f"{calendar.day_name[day]}: {', '.join(names)}\n"

    if birthdays_next_week:
        result += "Next week:\n"
        for day, names in birthdays_next_week.items():
            result += f"{calendar.day_name[day]}: {', '.join(names)}\n"


    return result.strip("\n")
