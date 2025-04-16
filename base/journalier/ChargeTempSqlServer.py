import pause
from datetime import  date,datetime,timedelta
delta = timedelta(days=1)


#print("\n charge_I_pmu \n")
#exec(open("C:\Batchs\scripts_python\chargements\charge_Ipmu.py").read())



    


#nextday = datetime.strptime((date.today()+delta).strftime('%Y%m%d'), '%Y%m%d').replace(hour=0, minute=10, second=0, microsecond=0)

#pause.until(nextday)


while True:
    
    
    
    
    #break
    
        
    
    import glob
    import os
    
    import pause
    from datetime import  date,datetime,timedelta
    delta = timedelta(days=1)
    
    Hour =  datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d').replace(hour=5, minute=0, second=0, microsecond=0)
    pause.until(Hour)
    
    
    #print(datetime.now())
        
    print(f"----------DEBUT DES CHARGEMENT:{str(datetime.now())}--------------------------")
    
    
    print("\n charge_HonoreGaming \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_HonoreGaming.py").read())
    
    import pause
    from datetime import  date,datetime,timedelta
    delta = timedelta(days=1)
    
    Hour =  datetime.strptime(date.today().strftime('%Y%m%d'), '%Y%m%d').replace(hour=5, minute=50, second=0, microsecond=0)
    pause.until(Hour)
    
    
    
    print("\n charge_Afitech_CommissionHistory \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_Afitech_CommissionHistory.py").read())
    
    print("\n charge_Afitech_DailyPaymentActivity \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_Afitech_DailyPaymentActivity.py").read())
    
    print("\n charge_Bwinners \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_Bwinners.py").read())
    
    print("\n charge_BWINNERS_GAMBIE \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_BWINNERS_GAMBIE.py").read())
    
    print("\n charge_DigitainAcajou \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_DigitainAcajou.py").read())
    
    
    print("\n charge_ALR_GITECH \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_ALR_GITECH.py").read())
    
    
    
    #print("\n charge_OnlineSunubet \n")
    #exec(open("C:\Batchs\scripts_python\chargements\charge_OnlineSunubet.py").read())
    
    
    
    
    
    
    
    
    #print("\n charge_CasinoLonasebet \n")
    #exec(open("C:\Batchs\scripts_python\chargements\charge_CasinoLonasebet.py").read())
    
    
    import pandas as pd
    import numpy as np
    #import pymssql
    import glob
    import shutil
    import pyodbc
    
    
    # In[5]:
    
    
    filesInitialDirectory = r"K:\DATA_FICHIERS\LONASEBET\CASINO\\"
    
    dest = 'K:\DATA_FICHIERS\LONASEBET\CASINO\OLD\\'
    
    
    SERVER = 'SRVSQLDWHPRD'
    DATABASE = 'DWHPR_TEMP'
    USERNAME = 'OPTIWARETEMP'
    PASSWORD = 'optiwaretemp'
    connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
    conn = pyodbc.connect(connectionString)
    cursor = conn.cursor()
    
    
    # suppression de la table temporaire
    cursor.execute(""" truncate table [DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_CASINO_LONASEBET] """)
    conn.commit()
    
    print("la table temporaire a ete videe")
    
    
    
    for file in glob.glob(filesInitialDirectory+"casinoLonasebet*csv"):
        #print(file)
        data = pd.read_csv(file,sep=';',index_col=False)
        namefile = file.split("\\")[-1]
        #print(data.columns)
        
        #if 'Grattage' in namefile:
    
        data = pd.DataFrame(data,columns=["JOUR","Stake","PaidAmount"])
        
        #print( len(['Username', 'Balance', 'Total Players','Total Players Date Range', 'SB Bets No.', 'SB Stake','SB Closed Stake', 'SB Wins No.', 'SB Wins', 'SB Ref No.', 'SB Refunds','SB GGR', 'Cas.Bets No.', 'Cas.Stake', 'Cas.Wins No.', 'Cas.Wins','Cas.Ref No.', 'Cas.Refunds', 'Cas.GGR', 'Total GGR', 'Adjustments','Deposits', 'Financial Deposits', 'Financial Withdrawals','Transaction Fee', 'date']) )
        
        #print(data.columns)
    
        data = data.replace(np.nan, '')
        data=data.astype(str)
        data = list(data.to_records(index=False))
    
        #print(data)
    
        data = [tuple(i) for i in data]
        #print(data[:5])
        
        
        #break
        
        #Insertion au niveau de la table temporaire
        #cursor.executemany("""INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_PREMIERBET]("SB Stake", "SB Refunds","SB Bets No.", "SB Ref No.","SB Wins No.", "SB Wins", "SB GGR", "Cas.Bets No.", "Cas.Stake", "Cas.Wins No.", "Cas.Wins","Cas.Ref No.", "Cas.Refunds", "Cas.GGR", "date") VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", data)
        #cursor.executemany("""INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_PREMIERBET]('Unnamed: 0', 'Username', 'Balance', 'Total Players','Total Players Date Range', 'SB Bets No.', 'SB Stake','SB Closed Stake', 'SB Wins No.', 'SB Wins', 'SB Ref No.', 'SB Refunds','SB GGR', 'Cas.Bets No.', 'Cas.Stake', 'Cas.Wins No.', 'Cas.Wins','Cas.Ref No.', 'Cas.Refunds', 'Cas.GGR', 'Total GGR', 'Adjustments','Deposits', 'Financial Deposits', 'Financial Withdrawals','Transaction Fee', 'date') VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", data)
        cursor.executemany("""INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_CASINO_LONASEBET] ("date","Mise Totale", "Somme PayÃ©e") VALUES(?, ?, ?)""", data)
        
        
        
        # Insertion au niveau de la table temporaire
        #cursor.executemany("""INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_PREMIERBET](CREATE_TIME,PRODUCT,STAKE,"MAX PAYOUT") VALUES(%s, %s, %s, %s)""", data)
        #cursor.executemany("""INSERT INTO [DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_PREMIERBET]("SB Stake", "SB Refunds","SB Bets No.", "SB Ref No.","SB Wins No.", "SB Wins", "SB GGR", "Cas.Bets No.", "Cas.Stake", "Cas.Wins No.", "Cas.Wins","Cas.Ref No.", "Cas.Refunds", "Cas.GGR", "date") VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""", data)
        conn.commit()
        print("le fichier a ete insere au niveau de la table temporaire")
        
        #namefile = file.split("\\")[-1]
        try:
            
            shutil.move(file,dest+namefile)
            
        except:
            os.remove(dest+namefile)
            shutil.move(file,dest+namefile)
        print(dest+namefile)
    
    cursor.close()
    conn.close()  
    
    
    
    
    
    
    print("\n charge_VirtuelAmabel \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_VirtuelAmabel.py").read())
    
    print("\n charge_zeturf \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_zeturf.py").read())
    
    print("\n charge_OnlineLonasebet \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_OnlineLonasebet.py").read())

    print("\n load_casino_gitech \n")
    exec(open("C:\Batchs\scripts_python\chargements\load_casino_gitech.py").read())
    
    print("\n charge_Acajou_Grattage \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_Acajou_Grattage.py").read())
    
    print("\n charge_Acajou_Pick3 \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_Acajou_Pick3.py").read())
    
    print("\n charge_Parifoot_Online \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_Parifoot_Online.py").read())
    
    print("\n charge_I_pmu \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_Ipmu.py").read())
    
    
    print("\n charge_Acajou_Mojabet_USSD \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_Acajou_Mojabet_USSD.py").read())
    
    
    
    
    print("\n charge_OnlineSunubet \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_OnlineSunubet.py").read())
    
    print("\n charge_CasinoSunubet \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_CasinoSunubet.py").read())
    
    print("\n charge_pmusenegal_ca \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_pmusenegal_ca.py").read())
    
    print("\n charge_pmusenegal_lots \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_pmusenegal_lots.py").read())
    
    print("\n charge_MiniShop \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_mini.py").read())


    print("\n charge_gitech- PARI \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_gitech- PARI.py").read())


    print("\n charge_pari_amabel \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_pari_amabel.py").read())
    
    
    print("\n charge_pari_honoregaming \n")
    exec(open("C:\Batchs\scripts_python\chargements\charge_pari_honoregaming.py").read())
    

    
    import pandas as pd
    import numpy as np
    import pyodbc
    import glob
    import shutil
    
    SERVER = 'SRVSQLDWHPRD'
    DATABASE = 'DWHPR_TEMP'
    USERNAME = 'OPTIWARETEMP'
    PASSWORD = 'optiwaretemp'
    connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
    conn = pyodbc.connect(connectionString)
    cursor = conn.cursor()
    
    
    # suppression de la table temporaire
    cursor.execute(""" truncate table [DWHPR_TEMP].[OPTIWARETEMP].[src_prd_sunubet_online] """)
    conn.commit()
    
    cursor.execute(""" truncate table [DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_SUNUBET_CASINO] """)
    conn.commit()


    # suppression de la table temporaire
    cursor.execute(""" MERGE INTO [DWHPR].[USER_DWHPR].DTM_MISE_SUNUBET_ONLINE t using
(
    select 
          m.idtemps as IDTEMPS,
          m.anneec as ANNEE,
          m.moisc as MOIS,
          w.ISSUEDATETIME as JOUR,
          sum (  CAST(replace(replace(ISNULL(w.stake,0),' ',''),',','.') as float) ) as CA,
                  upper('CASINO') as CATEGORIE,
          sum ( CAST(replace(replace(ISNULL(w.PAIDAMOUNT,0),' ',''),',','.') as float) ) as LOT,
          cast(0 as float) as MONTANT_ANNULE
          
    from [DWHPR_TEMP].[OPTIWARETEMP].SRC_PRD_SUNUBET_CASINO w ,[DWHPR].[USER_DWHPR].dim_temps m
    where  CAST(m.jour as date) =  CAST(w.ISSUEDATETIME as date)
    /* and to_date(trim(substr(w.issuedatetime,1,10))) BETWEEN '15/09/2023' AND '31/12/2023' */
    group by IDTEMPS, m.anneec, 
    m.moisc, w.ISSUEDATETIME          
) g
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour AND T.CATEGORIE = G.CATEGORIE) 
WHEN MATCHED THEN UPDATE SET t.CA=g.CA, T.LOTS = G.LOT, t.MONTANT_ANNULE = 0 
WHEN NOT MATCHED THEN
    INSERT (IDTEMPS,ANNEE,MOIS,JOUR,CA,LOTS,CATEGORIE,MONTANT_ANNULE) 
    VALUES (G.IDTEMPS, G.ANNEE,G.MOIS,G.JOUR,G.CA,G.LOT,G.CATEGORIE,0);  """)
    conn.commit()
    
    
    cursor.execute(""" MERGE INTO [DWHPR].[USER_DWHPR].DTM_MISE_SUNUBET_ONLINE t using
(
    select 
          m.idtemps as IDTEMPS,
           m.anneec as ANNEE,
          m.moisc as MOIS,
          w.ISSUEDATETIME as JOUR,  --CAST(replace(replace(ISNULL(w.PAIDAMOUNT,0),' ',''),',','.') as float)
          sum ( case when upper(w.FREEBET) in ('FALSE') then CAST(replace(replace(ISNULL(w.stake,0),' ',''),',','.') as float)
                       else cast(0 as float)
                  end ) as CA,
          /*case when upper(w.BetCategoryType) like upper('%SPORTS%') then 'PARIFOOT'
                       else  'VIRTUEL'
                  end as CATEGORIE,*/
                  upper(w.BetCategoryType) as CATEGORIE,
          sum ( CAST(replace(replace(ISNULL(w.PAIDAMOUNT,0),' ',''),',','.') as float) ) as LOT,
          cast(0 as float) as MONTANT_ANNULE
          
    from [DWHPR_TEMP].[OPTIWARETEMP].src_prd_sunubet_online w ,[DWHPR].[USER_DWHPR].dim_temps m
    where  CAST(m.jour as date) =  CAST(w.ISSUEDATETIME as date)
    /* and to_date(trim(substr(w.JOUR,1,10))) BETWEEN '15/09/2023' AND '31/12/2023' */
    group by IDTEMPS, m.anneec, 
    m.moisc
    ,w.ISSUEDATETIME, upper(w.BetCategoryType)          
) g
ON (t.annee = g.annee and t.mois=g.mois and t.jour=g.jour AND T.CATEGORIE = G.CATEGORIE) 
WHEN MATCHED THEN UPDATE SET t.CA=g.CA, T.LOTS = G.LOT, t.MONTANT_ANNULE = 0 
WHEN NOT MATCHED THEN
    INSERT (IDTEMPS,ANNEE,MOIS,JOUR,CA,LOTS,CATEGORIE,MONTANT_ANNULE) 
    VALUES (G.IDTEMPS, G.ANNEE,G.MOIS,G.JOUR,G.CA,G.LOT,G.CATEGORIE,0);   """)
    conn.commit()

    cursor.execute(""" truncate table [DWHPR_TEMP].[OPTIWARETEMP].[src_prd_sunubet_online] """)
    conn.commit()
    
    cursor.execute(""" truncate table [DWHPR_TEMP].[OPTIWARETEMP].[SRC_PRD_SUNUBET_CASINO] """)
    conn.commit()


    


    
    
    import gc
    gc.collect()

    
        
        
    import pause
    from datetime import  date,datetime,timedelta
    delta = timedelta(days=1)
    
    print(f"----------FIN DES CHARGEMENT:{str(datetime.now())}--------------------------")
    
    
    nextday = datetime.strptime((date.today()+delta).strftime('%Y%m%d'), '%Y%m%d').replace(hour=0, minute=10, second=0, microsecond=0)

    pause.until(nextday)
    
     
    