
from datetime import  date, timedelta, datetime
import time


def sleep(seconds):
    time.sleep(seconds)

def get_yesterday_date():
    yesterday_date = date.today() - timedelta(days=1)
    year = yesterday_date.strftime("%Y")
    month = yesterday_date.strftime("%m")
    day = yesterday_date.strftime("%d")
    return year, month, day, yesterday_date

def get_previous_month_date_range():
    today = date.today()
    first_day_current_month = today.replace(day=1)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)

    start_date = first_day_previous_month
    end_date = last_day_previous_month

    return start_date, end_date

def date_string_to_date(date_str, format="%Y-%m-%d"):
    try:
       return datetime.strptime(date_str, format).date()
    except :
        return None
