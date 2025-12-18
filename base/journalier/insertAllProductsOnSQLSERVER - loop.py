from datetime import date,timedelta #,datetime,timedelta
import datetime
import glob


delta = datetime.timedelta(days=1)
end_date = datetime.date.today()
start_date = end_date - delta

#print(start_date)
start_date = datetime.date(2025, 2, 25)
end_date = start_date+delta
#end_date = datetime.date(2024, 9, 1)

debut = start_date
fin = end_date-delta

generalDirectory = r"K:\\DATA_FICHIERS\\"


def transfert(source,destination):
    import shutil
    
    filename = source.split("\\")[-1]

    shutil.move(source, destination+filename)
    

   
print("-------ACAJOU---------------")

#while start_date<end_date:

directory = generalDirectory+r"ACAJOU\PICK3\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
#file = glob.glob(directory+f"**\\Listing_Tickets_Pick3 {str(start_date).replace('-','')}.csv",recursive=True)
file = glob.glob(directory+f"**\\Listing_Tickets_Pick3 {str(start_date).replace('-','')}_{str(start_date).replace('-','')}.csv",recursive=True)
 
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier Acajou Pick3 du {start_date} n'a pas ete extrait ")
else:
    transfert(file[0],directory)

directory = generalDirectory+r"ACAJOU\GRATTAGE\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
#file = glob.glob(directory+f"**\\Listing_Tickets_Grattage {str(start_date).replace('-','')}.csv",recursive=True)
file = glob.glob(directory+f"**\\Listing_Tickets_Grattage {str(start_date).replace('-','')}_{str(start_date).replace('-','')}.csv",recursive=True)

print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier Acajou Grattage du {start_date} n'a pas ete extrait ")
else:
    transfert(file[0],directory)

directory = generalDirectory+r"ACAJOU\DIGITAIN\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
file = glob.glob(directory+f"**\\Listing_Tickets_Sports_betting {str(start_date).replace('-','')}_{str(start_date).replace('-','')}.csv",recursive=True)

print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier Acajou DIGITAIN du {start_date} n'a pas ete extrait ")
else:
    transfert(file[0],directory)

print(start_date)

#start_date+=delta

print("-----------BWINNER-----------")

#while start_date<end_date:

directory = generalDirectory+r"BWINNERS\\"

file = glob.glob(directory+f"**\Bwinner_{str(start_date)}_{str(start_date)}.csv",recursive=True)

print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier Bwinner du {start_date} n'a pas ete extrait ")
else:
    transfert(file[0],directory)

print(start_date)

#start_date+=delta

print("-----------GITECH---------------")

#while start_date<end_date:

directory = generalDirectory+r"GITECH\ALR\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
file = glob.glob(directory+f"**\\GITECH {str(start_date)}.csv",recursive=True)

print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier ALR GITECH du {start_date} n'a pas ete extrait ")
else:
    transfert(file[0],directory)
    
directory = generalDirectory+r"GITECH\CASINO\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
file = glob.glob(directory+f"**\\GITECH CASINO {str(start_date)}.csv",recursive=True)
    
print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier CASINO GITECH du {start_date} n'a pas ete extrait ")
else:
    transfert(file[0],directory)

print(start_date)
#start_date+=delta

print("-----------HONOREGAMING------------------")

directory = generalDirectory+r"HONORE_GAMING\\"

#while start_date<end_date:

file = glob.glob(directory+f"**\\daily-modified-horse-racing-tickets-detailed_{str(start_date+delta).replace('-','')}.csv",recursive=True)

print( len( file ) )

if len( file )>0:
    transfert(file[0],directory)
else:
    print(f"le fichier de la date du {start_date} est manquant")
                 
print(start_date)

#start_date+=delta

print("-----------LONASEBET------------------")

#while start_date<end_date:

directory = generalDirectory+r"LONASEBET\ALR_PARIFOOT\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
file = glob.glob(directory+f"**\\OnlineLonasebet {str(start_date)}.csv",recursive=True)

print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier ALR LONASEBET du {start_date} n'a pas ete extrait ")
else:
    transfert(file[0],directory)
    
directory = generalDirectory+r"LONASEBET\CASINO\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
file = glob.glob(directory+f"**\\casinoLonasebet {str(start_date)}.csv",recursive=True)

print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier CASINO Lonasebet  du {start_date} n'a pas ete extrait ")
else:
    transfert(file[0],directory)
    
print(start_date)

#start_date+=delta


print("--------------PARIFOOT ONLINE----------------")

directory = generalDirectory+r"PARIFOOT_ONLINE\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
firstDay = datetime.date((end_date -  delta).year, (end_date -  delta).month, 1)

data = []

#while start_date<end_date:

file = glob.glob(directory+f"**\\ParifootOnline {str(start_date)}.csv",recursive=True)

if len( file )>0:
    transfert(file[0],directory)
    
    print(start_date)
    
else:
    print(f"le fichier de la date du {start_date} est manquant")

#start_date+=delta


print("--------------VIRTUEL AMABEL--------------------")

#while start_date<end_date:
directory = generalDirectory+r"VIRTUEL_AMABEL\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
file = glob.glob(directory+f"**\\virtuelAmabel{str(start_date)}.csv",recursive=True)

print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier virtuelAmabel du {start_date} n'a pas ete extrait ")
else:
    transfert(file[0],directory)

print(start_date)

#start_date+=delta

print("----------------------ZETURF---------------------------")

#while start_date<end_date:
directory = generalDirectory+r"ZETURF\\"

file = glob.glob(directory+f"**\ZEturf {str(start_date)}.csv",recursive=True)

print( len( file ) )

if len( file ) == 0:
    print(f"Le fichier Zeturf du {start_date} n'a pas ete extrait ")
else:
    transfert(file[0],directory)

print(start_date)

#start_date+=delta










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







import pyodbc

SERVER = 'SRVSQLDWHPRD'
DATABASE = 'DWHPR'
USERNAME = 'USER_DWHPR'
PASSWORD = 'optiware2016'
connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
conn = pyodbc.connect(connectionString)
cursor = conn.cursor()


print("PROC_ACAJOU")
cursor.execute("""
EXECUTE [USER_DWHPR].[PROC_ACAJOU];
""")
conn.commit()

'''
cursor.execute("""
EXECUTE [USER_DWHPR].[PROC_AFITECH];
""")
conn.commit()
'''
print("PROC_GITECH")
cursor.execute("""
EXECUTE [USER_DWHPR].[PROC_GITECH];
""")
conn.commit()
print("PROC_BWINNERS")
cursor.execute("""
EXECUTE [USER_DWHPR].[PROC_BWINNERS];
""")
conn.commit()
print("PROC_PARIFOOT_ONLINE")
cursor.execute("""
EXECUTE [USER_DWHPR].[PROC_PARIFOOT_ONLINE];
""")
conn.commit()
print("PROC_VIRTUEL_AMABEL")
cursor.execute("""
EXECUTE [USER_DWHPR].[PROC_VIRTUEL_AMABEL];
""")
conn.commit()
print("PROC_ZETURF")
cursor.execute("""
EXECUTE [USER_DWHPR].[PROC_ZETURF];
""")
conn.commit()
print("PROC_NEW_PRODUIT")
cursor.execute("""
EXECUTE [USER_DWHPR].[PROC_NEW_PRODUIT];
""")
conn.commit()
print("PROC_HONORE_GAMING")
cursor.execute("""
EXECUTE [USER_DWHPR].[PROC_HONORE_GAMING]
""")
conn.commit()

cursor.close()
conn.close()  

#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]




























    


'''
    
print("-------ACAJOU---------------")

while start_date<end_date:
    
    directory = generalDirectory+r"ACAJOU\PICK3\\"
    #print(f"virtuelAmabel{str(start_date)}.csv")
    #file = glob.glob(directory+f"**\\Listing_Tickets_Pick3 {str(start_date).replace('-','')}.csv",recursive=True)
    file = glob.glob(directory+f"**\\Listing_Tickets_Pick3 {str(start_date).replace('-','')}_{str(start_date).replace('-','')}.csv",recursive=True)
 
    print( len( file ) )

    if len( file ) == 0:
        print(f"Le fichier Acajou Pick3 du {start_date} n'a pas ete extrait ")
    else:
        transfert(file[0],directory)

    directory = generalDirectory+r"ACAJOU\GRATTAGE\\"
    #print(f"virtuelAmabel{str(start_date)}.csv")
    #file = glob.glob(directory+f"**\\Listing_Tickets_Grattage {str(start_date).replace('-','')}.csv",recursive=True)
    file = glob.glob(directory+f"**\\Listing_Tickets_Grattage {str(start_date).replace('-','')}_{str(start_date).replace('-','')}.csv",recursive=True)
    
    print( len( file ) )

    if len( file ) == 0:
        print(f"Le fichier Acajou Grattage du {start_date} n'a pas ete extrait ")
    else:
        transfert(file[0],directory)
    
    directory = generalDirectory+r"ACAJOU\DIGITAIN\\"
    #print(f"virtuelAmabel{str(start_date)}.csv")
    file = glob.glob(directory+f"**\\Listing_Tickets_Sports_betting {str(start_date).replace('-','')}_{str(start_date).replace('-','')}.csv",recursive=True)

    print( len( file ) )

    if len( file ) == 0:
        print(f"Le fichier Acajou DIGITAIN du {start_date} n'a pas ete extrait ")
    else:
        transfert(file[0],directory)
    
    print(start_date)
    
    start_date+=delta

print("-----------BWINNER-----------")

while start_date<end_date:
    
    directory = generalDirectory+r"BWINNERS\\"

    file = glob.glob(directory+f"**\Bwinner_{str(start_date)}_{str(start_date)}.csv",recursive=True)

    print( len( file ) )

    if len( file ) == 0:
        print(f"Le fichier Bwinner du {start_date} n'a pas ete extrait ")
    else:
        transfert(file[0],directory)
    
    print(start_date)
    
    start_date+=delta

print("-----------GITECH---------------")

while start_date<end_date:

    directory = generalDirectory+r"GITECH\ALR\\"
    #print(f"virtuelAmabel{str(start_date)}.csv")
    file = glob.glob(directory+f"**\\GITECH {str(start_date)}.csv",recursive=True)

    print( len( file ) )

    if len( file ) == 0:
        print(f"Le fichier ALR GITECH du {start_date} n'a pas ete extrait ")
    else:
        transfert(file[0],directory)
        
    directory = generalDirectory+r"GITECH\CASINO\\"
    #print(f"virtuelAmabel{str(start_date)}.csv")
    file = glob.glob(directory+f"**\\GITECH CASINO {str(start_date)}.csv",recursive=True)
        
    print( len( file ) )
    
    if len( file ) == 0:
        print(f"Le fichier CASINO GITECH du {start_date} n'a pas ete extrait ")
    else:
        transfert(file[0],directory)
    
    print(start_date)
    start_date+=delta

print("-----------HONOREGAMING------------------")

directory = generalDirectory+r"HONORE_GAMING\\"

while start_date<end_date:
    
    file = glob.glob(directory+f"**\\daily-modified-horse-racing-tickets-detailed_{str(start_date+delta).replace('-','')}.csv",recursive=True)

    print( len( file ) )
    
    if len( file )>0:
        transfert(file[0],directory)
    else:
        print(f"le fichier de la date du {start_date} est manquant")
                     
    print(start_date)
    
    start_date+=delta
    
print("-----------LONASEBET------------------")

while start_date<end_date:

    directory = generalDirectory+r"LONASEBET\ALR_PARIFOOT\\"
    #print(f"virtuelAmabel{str(start_date)}.csv")
    file = glob.glob(directory+f"**\\OnlineLonasebet {str(start_date)}.csv",recursive=True)

    print( len( file ) )

    if len( file ) == 0:
        print(f"Le fichier ALR LONASEBET du {start_date} n'a pas ete extrait ")
    else:
        transfert(file[0],directory)
        
    directory = generalDirectory+r"LONASEBET\CASINO\\"
    #print(f"virtuelAmabel{str(start_date)}.csv")
    file = glob.glob(directory+f"**\\casinoLonasebet {str(start_date)}.csv",recursive=True)

    print( len( file ) )

    if len( file ) == 0:
        print(f"Le fichier CASINO Lonasebet  du {start_date} n'a pas ete extrait ")
    else:
        transfert(file[0],directory)
        
    print(start_date)
    
    start_date+=delta
    

print("--------------PARIFOOT ONLINE----------------")

directory = generalDirectory+r"PARIFOOT_ONLINE\\"
#print(f"virtuelAmabel{str(start_date)}.csv")
firstDay = datetime.date((end_date -  delta).year, (end_date -  delta).month, 1)

data = []

while start_date<end_date:
    
    file = glob.glob(directory+f"**\\ParifootOnline {str(start_date)}.csv",recursive=True)
    
    if len( file )>0:
        transfert(file[0],directory)
        
        print(start_date)
        
    else:
        print(f"le fichier de la date du {start_date} est manquant")
    
    start_date+=delta
    
    
print("--------------VIRTUEL AMABEL--------------------")

while start_date<end_date:
    directory = generalDirectory+r"VIRTUEL_AMABEL\\"
    #print(f"virtuelAmabel{str(start_date)}.csv")
    file = glob.glob(directory+f"**\\virtuelAmabel{str(start_date)}.csv",recursive=True)
    
    print( len( file ) )

    if len( file ) == 0:
        print(f"Le fichier virtuelAmabel du {start_date} n'a pas ete extrait ")
    else:
        transfert(file[0],directory)
    
    print(start_date)
    
    start_date+=delta
    
print("----------------------ZETURF---------------------------")

while start_date<end_date:
    directory = generalDirectory+r"ZETURF\\"

    file = glob.glob(directory+f"**\ZEturf {str(start_date)}.csv",recursive=True)

    print( len( file ) )

    if len( file ) == 0:
        print(f"Le fichier Zeturf du {start_date} n'a pas ete extrait ")
    else:
        transfert(file[0],directory)
    
    print(start_date)
    
    start_date+=delta

'''