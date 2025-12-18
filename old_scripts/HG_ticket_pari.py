#!/usr/bin/env python
# coding: utf-8

# In[34]:


from datetime import date,timedelta #,datetime,timedelta
import datetime

import pandas as pd
import numpy as np

import glob


# In[35]:




agence = pd.read_csv(r"K:\DATA_FICHIERS\HONORE_GAMING\PARI\Pari_avec_agence\to_save\bonne_affectation_hg.csv",sep=';',encoding='latin-1',index_col=False)

mise = pd.read_csv(r"K:\DATA_FICHIERS\HONORE_GAMING\PARI\Pari_avec_agence\to_save\mise_unitaire.csv",sep=';',encoding='latin-1',index_col=False)


# In[36]:



source = r'K:\DATA_FICHIERS\HONORE_GAMING\\'

directory = "K:\DATA_FICHIERS\HONORE_GAMING\PARI\Pari_avec_agence\\"


delta = datetime.timedelta(days=1)
end_date = datetime.date.today()
start_date = end_date #- delta

#print(start_date)
#start_date = datetime.date(2025, 4, 4)
#end_date = start_date#+delta
#end_date = datetime.date(2025, 4, 6)


while start_date<=end_date:
    notdone = False
    jour = (start_date).strftime("%Y%m%d")
    #print(jour)
    #for file in glob.glob(source+'daily-modified-horse-racing-tickets-detailed_'+f"{jour}*.csv"):
    file = glob.glob(source+f'**\daily-modified-horse-racing-tickets-detailed_'+f"{jour}*.csv",recursive=True)
    #print(file)
    file = file[0]
    #print(file)
    
    #break
        
        
        
    cols_to_import = ['TerminalDescription','RetailCategoryName','ReportDateTime','State', 'MeetingDate', 'BetType', 'TotalStake','GameName','PayableAmount','PaidAmount'] #, 'BetCategoryName' -- ,'PayableAmount'

    #print(file)
    df = pd.read_csv(file,sep=';',encoding='latin-1',index_col=False,usecols=cols_to_import)

    df = pd.merge(agence, df, on='RetailCategoryName', how='right')

    df = pd.merge(mise, df, on=['BetType','GameName'], how='right')

    # Define conditions with contains
    conditions = [
        (df['GameName'].str.upper().str.contains('ALR')),  # GameName contains 'ALR'
        (df['GameName'].str.upper().str.contains('PLR')),  # GameName contains 'PLR'
        (df['GameName'].str.upper().str.contains('MCI')) & df['BetType'].str.upper().str.contains('|'.join(['SIMPLE', 'COUPLE', 'TRIO'])),  # BetType contains any of these
        (df['GameName'].str.upper().str.contains('MCI')) & df['BetType'].str.upper().str.contains('|'.join(['MULTI', 'QUINTE', 'QUARTE','TIERCE']))  # BetType contains any of these
    ]

    # Define corresponding outputs
    choices = ['ALR', 'PLR', 'PLR', 'ALR']

    # Apply the conditions to create a new column
    df['CATEGORIE_FINALE'] = np.select(conditions, choices, default='Unknown')



    #print(df.dtypes)

    #print(df['ReportDateTime'].iloc[0],df['MeetingDate'].iloc[0])

    #print(df)

    #df['PayableAmount'] = df['PayableAmount'].str.replace(',', '.').astype(float)

    try:

        df['TotalStake'] = df['TotalStake'].str.replace(',', '.').astype(float)
    except:
        pass

    try:

        df['PayableAmount'] = df['PayableAmount'].str.replace(',', '.').astype(float)
    except:
        pass

    try:

        df['PaidAmount'] = df['PaidAmount'].str.replace(',', '.').astype(float)
    except:
        pass

    
    df['MeetingDate'] = df['MeetingDate'].astype(str)

    date_str_1 = (start_date - delta).strftime("%d/%m/%Y")  # Format as 'dd/mm/yyyy'
    date_str_2 = str(start_date - delta)  # Convert the date to string in ISO format

    # Filter rows where MeetingDate contains either of the formatted date strings
    df = df[df['MeetingDate'].str.contains(date_str_1, regex=True) | 
             df['MeetingDate'].str.contains(date_str_2, regex=True)]

    #df = df[df['MeetingDate'].str.contains(str(start_date-delta), regex=True).any() || df['MeetingDate'].str.contains((start_date-delta).strftime("%d/%m/%Y"), regex=True).any()]

    if(len(df)==0):
        print("DataFrame is empty!")
        start_date+=delta
        continue
        #break


    #df['ANNULATION'] = np.where(df['State'].str.lower().isin(['cancelled']), df['TotalStake'], np.nan)
    df['ANNULATION'] = np.where(df['State'].str.lower().isin(['cancelled']), df['TotalStake'], np.nan)

    df['TICKET_VENDU'] = df['TotalStake'] / df['MinTotalStake']

    df['TICKET_ANNULE'] = df['ANNULATION'] / df['MinTotalStake'] #np.where(df['State'].str.lower().isin(['cancelled']), df['TICKET_VENDU'], np.nan)



    '''
    #df['PayableAmount'] = np.where(df['GameName'].str.lower().isin(['mci']), 0, np.nan)
    df['PayableAmount'] = np.where(
df['GameName'].str.lower().fillna('').isin(['mci']),  # Exact match for 'mci' after lowercase
0,  # Set to 0 when condition is True
df['PayableAmount']  # Keep the existing PayableAmount value when condition is False
)
    '''



    df['CA'] = df['TotalStake'].fillna(0).astype(float)-df['ANNULATION'].fillna(0).astype(float)


    df = df.drop('State', axis=1)

    df = df.drop('ReportDateTime', axis=1)
    
    #print(df.columns)


    df = df.fillna(0)

    #namefile = 'HG_PARI_'+str(df['MeetingDate'].iloc[0])[:10]+'.csv'
    namefile = 'HG_PARI_'+str(start_date - delta)+'.csv'

    #print(namefile)

    df['Year'] = (start_date - delta).strftime("%Y")#df['MeetingDate'].dt.year
    #df['Month'] = (start_date - delta).strftime("%-m")#df['MeetingDate'].dt.month
    df['Month'] = int((start_date - delta).strftime("%m"))

    df['JOUR'] = (start_date - delta).strftime("%d/%m/%Y")


    #print(df['Year'])

    grouped_df = df.groupby(['Year','Month','JOUR','RetailCategoryName','AGENCE','TerminalDescription','CATEGORIE_FINALE' ,'GameName' ,'BetType','MinTotalStake']).sum()

    grouped_df.to_csv(directory+namefile, sep=';', encoding='latin-1',decimal=',')
    notdone = True

    start_date+=delta
    if notdone:
        print(f"Le fichier HONORE GAMING pari du {start_date - delta} a bien ete extrait")
    else:
        print(f"Le fichier HONORE GAMING pari du {start_date - delta} est introuvable")
#break


# In[37]:


#d = dir()

#You'll need to check for user-defined variables in the directory
#for obj in d:
for obj in dir():
    #checking for built-in variables/functions
    if not obj.startswith('__'):
        #deleting the said obj, since a user-defined function
        del globals()[obj]

