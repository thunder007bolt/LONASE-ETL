import sys
sys.path.append("/")

from base.orchestrator import Orchestrator
from extract_monthly import run_afitech_daily_payment_activity_monthly
from transform import run_afitech_daily_payment_activity_transformer
from load import run_afitech_daily_payment_activity_loader

def run_afitech_daily_payment_activity_monthly_orchestrator():
    orchestrator = Orchestrator(
        name="afitech_daily_payement_activity_monthly",
        extractor=run_afitech_daily_payment_activity_monthly,
        transformer=run_afitech_daily_payment_activity_transformer,
        loader=run_afitech_daily_payment_activity_loader
    )
    orchestrator.run()

if __name__ == "__main__":
    run_afitech_daily_payment_activity_monthly_orchestrator()