import os
import subprocess
import time
import shutil, sys
import gc
from datetime import date, datetime, timedelta
from te import SCRIPTS_DIR, JOURNALIER_DIR, run_script


def main_cycle():
    print("\n=== Debut ===\n")
    
    script_honore_gaming = os.path.join(SCRIPTS_DIR, "extract_HonoreGaming.py")
    script_hg_ticket_pari = os.path.join(SCRIPTS_DIR, "HG_ticket_pari.py")
    script_insert_honore_oracle = os.path.join(JOURNALIER_DIR, "insertHonoregamingOnOracleDatabase.py")
    #run_script(script_honore_gaming)
    run_script(script_hg_ticket_pari)
    run_script(script_insert_honore_oracle)
    '''
    '''
    print("\n=== Fin ===\n")
    exit(0)    


if __name__ == "__main__":
    main_cycle()