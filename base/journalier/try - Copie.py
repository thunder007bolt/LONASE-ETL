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

#a = 5/0

#print(a)

import pause
from datetime import  date,datetime,timedelta
delta = timedelta(days=1)


#subprocess.Popen(['python', "C:\Batchs\scripts_python\extractions\extract_DigitainAcajou.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)


#process = subprocess.Popen(['ping', 'google.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

#subprocess.Popen("C:\Batchs\scripts_python\extractions\extract_parifoot_online.py",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)


'''
print("\n extract_acajouGrattage \n")
exec(open("C:\Batchs\scripts_python\extractions\extract_acajouGrattage-bis.py").read())

print("\n extract_acajouPick3 \n")
exec(open("C:\Batchs\scripts_python\extractions\extract_acajouPick3-bis.py").read())

'''



nextday = datetime.strptime((date.today()+delta).strftime('%Y%m%d'), '%Y%m%d').replace(hour=0, minute=10, second=0, microsecond=0)

pause.until(nextday)
    


while True:
    
    #break
    
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
        
    import os
    os.system("taskkill /im excel.exe /f")
    
    #break

    delta = timedelta(days=1)
    #filesInitialDirectory = r"C:\Batchs\scripts_python\extractions\\"
    
    import pause
    from datetime import  date,datetime,timedelta

    Hour =  datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d').replace(hour=2, minute=0, second=0, microsecond=0)
    pause.until(Hour)
    
    print("\n extract_HonoreGaming \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_HonoreGaming.py").read())
    
    print("\n insertHonoregamingOnOracle \n")
    #exec(open(r"C:\Batchs\scripts_python\extractions\journalier\upload_HonoreGaming_oracle.py").read())
    
    exec(open(r"C:\Batchs\scripts_python\extractions\journalier\insertHonoregamingOnOracleDatabase.py", encoding='utf-8').read())
    
    
    break
    
    
    
    #"""
    
    
    #print(Hour1)
    #print(Hour11)
    #print(nextday)
    #while not(datetime.now() >= datetime.now().replace(hour=00, minute=15, second=0, microsecond=0) and datetime.now() <= datetime.now().replace(hour=22, minute=59, second=0, microsecond=0)) :
    #while False:
        #time.sleep(60)
        
    
    import pause
    from datetime import  date,datetime,timedelta

    Hour1 =  datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d').replace(hour=4, minute=45, second=0, microsecond=0)
    pause.until(Hour1)
    
    #'''
    
    import os
    import subprocess
    
    print("\n extract_afitech - CommissionHistory \n")
    #exec(open("C:\Batchs\scripts_python\extractions\extract_afitech - CommissionHistory.py").read())
    #afch = subprocess.Popen(['python', "C:\Batchs\scripts_python\extractions\extract_afitech - CommissionHistory.py"])
    subprocess.Popen(['python', "C:\Batchs\scripts_python\extractions\extract_afitech - CommissionHistory.py"]) #afch = 
    #subprocess.Popen("extract_afitech - CommissionHistory.py",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    
    import os
    import subprocess
    
    print("\n extract_afitech - DailyPaymentActivity \n")
    #exec(open("C:\Batchs\scripts_python\extractions\extract_afitech - DailyPaymentActivity.py").read())
    #subprocess.Popen("extract_afitech - CommissionHistory.py",shell=True,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    #afdp = subprocess.Popen(['python', "C:\Batchs\scripts_python\extractions\extract_afitech - DailyPaymentActivity.py"])
    subprocess.Popen(['python', "C:\Batchs\scripts_python\extractions\extract_afitech - DailyPaymentActivity.py"])
    
    #ap3 = subprocess.Popen(['python', "C:\Batchs\scripts_python\extractions\extract_acajouPick3.py"])
    #subprocess.Popen(['python', "C:\Batchs\scripts_python\extractions\extract_acajouPick3 bis.py"])
    
    #agt = subprocess.Popen(['python', "C:\Batchs\scripts_python\extractions\extract_acajouGrattage.py"])
   # subprocess.Popen(['python', "C:\Batchs\scripts_python\extractions\extract_acajouGrattage - bis.py"])
    
    #exec(open("C:\Batchs\scripts_python\extractions\extract_acajouGrattage.py").read())
    #exec(open("C:\Batchs\scripts_python\extractions\extract_acajouPick3.py").read())
    

    

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
    
    print("\n extract_Mojabet \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_Mojabet USSD.py").read())
    
    print("\n extract_i_pmu \n")
    #exec(open("C:\Batchs\scripts_python\extractions\extract_i_pmu.py").read())
    
    print("\n extract_parifoot_online \n")
    exec(open("C:\Batchs\scripts_python\extractions\extract_parifoot_online.py").read())
    


    
    print("\n extract_acajouGrattage \n")
    #exec(open("C:\Batchs\scripts_python\extractions\extract_acajouGrattage-bis.py").read())

    print("\n extract_acajouPick3 \n")
    #exec(open("C:\Batchs\scripts_python\extractions\extract_acajouPick3-bis.py").read())
    
    
    
    
    #exec(open("C:\Batchs\scripts_python\extractions\extract_acajouGrattage.py").read())
    #exec(open("C:\Batchs\scripts_python\extractions\extract_acajouPick3.py").read())
    
    
    
    

    
    #import pause
    #from datetime import  date,datetime,timedelta
    #Hour11 = datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d').replace(hour=8, minute=0, second=0, microsecond=0)

    #pause.until(Hour11)
    
    
    
    
    #"""
    
    
    #print("\n chargement sur oracle \n")
    #exec(open("C:\Batchs\scripts_python\extractions\journalier\insertAllProductsOnOracle.py").read())
    
    
    #break
    
    
    #print("\n extractPremierSn \n")
    #exec(open("C:\Batchs\scripts_python\extractions\extractPremierSn.py").read())
    
    
    import pause
    from datetime import  date,datetime,timedelta
    delta = timedelta(days=1)
    
    print(f"Ceci marque la fin des extractions journalieres du {str(datetime.now())}")
    
    
    nextday = datetime.strptime((date.today()+delta).strftime('%Y%m%d'), '%Y%m%d').replace(hour=0, minute=10, second=0, microsecond=0)

    pause.until(nextday)
    
    

    
    