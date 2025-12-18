### system ###

from extract import ExtractAfitechDailyPaymentActivity
from utils.date_utils import get_previous_month_date_range


def run_afitech_daily_payment_activity_monthly():
    env_variables_list = ["AFITECH_LOGIN_USERNAME", "AFITECH_LOGIN_PASSWORD", "AFITECH_GET_OTP_URL"]
    start_date, end_date = get_previous_month_date_range()
    job = ExtractAfitechDailyPaymentActivity(env_variables_list, start_date, end_date)
    job.process_extraction()

if __name__ == "__main__":
    run_afitech_daily_payment_activity_monthly()
