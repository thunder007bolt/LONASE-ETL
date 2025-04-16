import os
import subprocess
import time
import glob
from datetime import  date,datetime,timedelta

import shutil
import gc
import pause

#from wakepy import set_keepawake, unset_keepawake

#set_keepawake(keep_screen_awake=False)



while True:
    
    import os
    import subprocess
    import time
    import glob
    from datetime import  date,datetime,timedelta
    
    import shutil
    import gc
    import pause
    
    try:
        shutil.rmtree(r"C:\Users\optiware\AppData\Local\Temp\gen_py\3.7")
    except OSError as o:
        print(f"Error, {o.strerror}:")
        
    
    #break

    delta = timedelta(days=1)
    #filesInitialDirectory = r"C:\Batchs\scripts_python\extractions\\"
    
    
    
    
    
    #print(Hour1)
    #print(Hour11)
    #print(nextday)
    #while not(datetime.now() >= datetime.now().replace(hour=00, minute=15, second=0, microsecond=0) and datetime.now() <= datetime.now().replace(hour=22, minute=59, second=0, microsecond=0)) :
    #while False:
        #time.sleep(60)
        
    
    import pause
    from datetime import  date,datetime,timedelta

    Hour1 =  datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d').replace(hour=5, minute=0, second=0, microsecond=0)
    pause.until(Hour1)
    
    #'''

    print("\n extract_HonoreGaming \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_HonoreGaming.py").read())
    
    

    print("\n extract_Bwinners \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_Bwinners.py").read())
    
    print("\n extract_Bwinner_GAMBIE \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_Bwinner_GAMBIE.py").read())
    

    print("\n extract_DigitainAcajou \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_DigitainAcajou.py").read())
    
    #'''
    

    print("\n extract_Financial \n")
    #exec(open("C:\Batchs\scripts_python\extractions\extract_Financial.py").read())
    

    print("\n extract_gitech \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_gitech.py").read())
    
    print("\n extraction_Casino_Gitech \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_CASINO_gitech.py").read())
    

    print("\n extract_virtuelAmabel \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_virtuelAmabel.py").read())
    

    print("\n extract_zeturf \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_zeturf.py").read())
    

    print("\n extract_zonebetting \n")
    #exec(open("C:\Batchs\scripts_python\extractions\extract_zonebetting.py").read())
    
    print("\n extract_afitech - CommissionHistory \n")
    #exec(open("C:\Batchs\scripts_python\extractions\extract_afitech - CommissionHistory.py").read())
    

    print("\n extract_afitech - DailyPaymentActivity \n")
    #exec(open("C:\Batchs\scripts_python\extractions\extract_afitech - DailyPaymentActivity.py").read())
    
    
    
    import pause
    from datetime import  date,datetime,timedelta
    #Hour8 = datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d').replace(hour=8, minute=30, second=0, microsecond=0)
    
    #pause.until(Hour8)

    print("\n extract_CasinoLonasebet \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_CasinoLonasebett.py").read())
    
    
    print("\n extract_OnlineLonasebet \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_OnlineLonasebett.py").read())
    
    
    print("\n extract_OnlineSunubet \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_OnlineSunubett.py").read())
    
    print("\n extract_CasinoSunubet \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_CasinoSunubett.py").read())
    
    print("\n extract_acajouGrattage \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_acajouGrattage.py").read())
    

    print("\n extract_acajouPick3 \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_acajouPick3.py").read())
    
    exec(open("C:\Batchs\scripts_python\extractions\extract_acajouGrattage.py").read())
    exec(open("C:\Batchs\scripts_python\extractions\extract_acajouPick3.py").read())
    
    
    
    

    
    import pause
    from datetime import  date,datetime,timedelta
    Hour11 = datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d').replace(hour=8, minute=0, second=0, microsecond=0)

    pause.until(Hour11)
    
    print("\n extract_parifoot_online \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_parifoot_online.py").read())
    
    #exec(open("C:\Batchs\scripts_python\extractions\journalier\insertAllProductsOnOracle.py").read())
    
    
    #print("\n extractPremierSn \n")
    #exec(open("C:\Batchs\scripts_python\extractions\extractPremierSn.py").read())
    
    
    import pause
    from datetime import  date,datetime,timedelta
    delta = timedelta(days=1)
    
    print(f"Ceci marque la fin des extractions journalieres du {date.today()}")
    
    
    nextday = datetime.strptime((date.today()+delta).strftime('%Y%m%d'), '%Y%m%d').replace(hour=0, minute=10, second=0, microsecond=0)

    pause.until(nextday)
    
    

    
    