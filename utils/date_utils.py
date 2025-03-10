import datetime, time

def sleep(seconds):
    time.sleep(seconds)

def get_yesterday_date():
    yesterday_date = datetime.date.today() - datetime.timedelta(days=1)
    year = yesterday_date.strftime("%Y")
    month = yesterday_date.strftime("%m")
    day = yesterday_date.strftime("%d")
    return year, month, day, yesterday_date
