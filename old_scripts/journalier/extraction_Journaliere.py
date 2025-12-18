

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


try:
    shutil.rmtree(r"C:\Users\optiware\AppData\Local\Temp\gen_py\3.7")
except OSError as o:
    print(f"Error, {o.strerror}:")



delta = timedelta(days=1)
filesInitialDirectory = r"C:\Batchs\scripts_python\extractions\\"

while True:
    
    Hour1 =  datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d').replace(hour=1, minute=0, second=0, microsecond=0)

    Hour11 = datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d').replace(hour=11, minute=0, second=0, microsecond=0)

    nextday = datetime.strptime((date.today()+delta).strftime('%Y%m%d'), '%Y%m%d').replace(hour=0, minute=10, second=0, microsecond=0)

    #while not(datetime.now() >= datetime.now().replace(hour=00, minute=15, second=0, microsecond=0) and datetime.now() <= datetime.now().replace(hour=22, minute=59, second=0, microsecond=0)) :
    #while False:
        #time.sleep(60)
    
    pause.until(Hour1)
    aa = 0

    
    for file in glob.glob(filesInitialDirectory+"*py"):
        if 'HonoreGaming' in file or 'parifoot_online' in file or 'PremierSn' in file or 'i_pmu' in file :
            continue
        #print(file)
        namefile = file.split("\\")[-1]
        
        if aa < 5 :
            continue	    

        print(namefile+"\n\n")

        exec(open(file).read())
        aa+=1

        print("\n\n")

        #break

    #today_50_minute = datetime.now().replace(hour=0, minute=50, second=0, microsecond=0)

    #while datetime.now() <= datetime.now().replace(hour=0, minute=50, second=0, microsecond=0) :

        #time.sleep(60)

    exec(open("C:\Batchs\scripts_python\extractions\extract_HonoreGaming.py").read())


    #while datetime.now() <= datetime.now().replace(hour=12, minute=00, second=0, microsecond=0) :

        #time.sleep(60)
    
    pause.until(Hour11)

    print("extract_parifoot_online \n\n")

    exec(open("C:\Batchs\scripts_python\extractions\extract_parifoot_online.py").read())

    print("\n\n")

    print("extractPremierSn \n\n")

    exec(open("C:\Batchs\scripts_python\extractions\extractPremierSn.py").read())

    print("\n\n")
    
    pause.until(nextday)

