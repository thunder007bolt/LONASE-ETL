
from datetime import  date, timedelta, datetime
import time

# Formats de date standardisés
DATE_FORMAT_DISPLAY = "%d/%m/%Y"  # Format d'affichage français
DATE_FORMAT_STORAGE = "%Y-%m-%d"  # Format de stockage ISO
DATE_FORMAT_FILENAME = "%Y%m%d"   # Format pour noms de fichiers


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
    except Exception:
        return None


def parse_date_multi(date_str, formats=("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y")):
    """
    Essaie plusieurs formats et renvoie une date ou None.
    """
    if date_str is None:
        return None
    for fmt in formats:
        try:
            return datetime.strptime(str(date_str).split(" ")[0], fmt).date()
        except Exception:
            continue
    return None
