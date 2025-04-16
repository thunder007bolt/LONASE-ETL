from datetime import date,timedelta #,datetime,timedelta
import datetime

import pandas as pd
import numpy as np

import glob

#source = r'\\192.168.1.103\Users\Admin\Desktop\HONORE_GAMING\ALL_FILES\\'
source = r'K:\DATA_FICHIERS\HONORE_GAMING\OLD\\'

directory = "K:\DATA_FICHIERS\HONORE_GAMING\PARI\\"

# \192.168.1.103\Users\Admin\Desktop\HONORE_GAMING\ALL_FILES\daily-modified-horse-racing-tickets-detailed_20240628.csv

for file in glob.glob(r'\\192.168.1.103\Users\Admin\Desktop\HONORE_GAMING\ALL_FILES\daily-modified-horse-racing-tickets-detailed_20240628.csv'):
    print(file)


delta = datetime.timedelta(days=1)
end_date = datetime.date.today()
start_date = end_date - delta

#print(start_date)
#start_date = datetime.date(2024, 2, 1)
#end_date = start_date+delta
#end_date = datetime.date(2024, 1, 13)


while start_date<end_date:
    jour = (start_date).strftime("%Y%m%d")
    print(jour)
    for file in glob.glob(source+'daily-modified-horse-racing-tickets-detailed_'+f"{jour}*.csv"):
        print(file)
        
        cols_to_import = ['ReportDateTime','State', 'MeetingDate', 'BetType', 'TotalStake','GameName'] #, 'BetCategoryName' -- ,'PayableAmount'

        df = pd.read_csv(file,sep=';',encoding='latin-1',index_col=False,usecols=cols_to_import)
        
        #print(df)

        #print(df)

        #df['PayableAmount'] = df['PayableAmount'].str.replace(',', '.').astype(float)

        df['TotalStake'] = df['TotalStake'].str.replace(',', '.').astype(float)

        #df['ReportDateTime'] = pd.to_datetime(df['ReportDateTime'], utc=True).dt.tz_localize(None)
        
        #df['ReportDateTime'] = pd.to_datetime(df['ReportDateTime'], utc=True).dt.normalize()
        
        df['ReportDateTime'] = pd.to_datetime(df['ReportDateTime'], errors='coerce', format='%d/%m/%Y %H:%M:%S').dt.normalize()

        
        #df['ReportDateTime'] = pd.to_datetime(df['ReportDateTime'], errors='coerce', format='%d/%m/%Y %H:%M')
        
        #df['ReportDateTime'] = pd.to_datetime(df['ReportDateTime'], errors='coerce',format='%d/%m/%Y').dt.normalize()
        
        df['MeetingDate'] = pd.to_datetime(df['MeetingDate'], errors='coerce', format='%Y-%m-%d')
        
        #print(df.dtypes)
        
        print(df['ReportDateTime'].iloc[0],df['MeetingDate'].iloc[0])
        
        #break
        print(df['ReportDateTime'])
        
        #print(df['MeetingDate'])
        
        #break
        # Optionally, strip the time part if you only care about the date
        #df['ReportDateTime'] = df['ReportDateTime'].dt.date
        #df['MeetingDate'] = df['MeetingDate'].dt.date

        #print(df['ReportDateTime'])

        # Convert 'second_column' to datetime
        #df['MeetingDate'] = pd.to_datetime(df['MeetingDate'], format='%d/%m/%Y')
        #df['MeetingDate'] = pd.to_datetime(df['MeetingDate'], utc=True)

        #print(df['MeetingDate'])

        df = df[df['ReportDateTime'] - df['MeetingDate'] == pd.Timedelta(days=1)]

        if(len(df)==0):
            print("DataFrame is empty!")
            break


        df['ANNULATION'] = np.where(df['State'].str.lower().isin(['cancelled']), df['TotalStake'], np.nan)

        df['TICKET_VENDU'] = 1

        df['TICKET_ANNULE'] = np.where(df['State'].str.lower().isin(['cancelled']), df['TICKET_VENDU'], np.nan)

        df['CA'] = df['TotalStake'].fillna(0).astype(float)-df['ANNULATION'].fillna(0).astype(float)


        df = df.drop('State', axis=1)

        df = df.drop('ReportDateTime', axis=1)


        df = df.fillna(0)

        namefile = 'HG_PARI_'+str(df['MeetingDate'].iloc[0])[:10]+'.csv'

        print(namefile)

        df['Year'] = df['MeetingDate'].dt.year
        df['Month'] = df['MeetingDate'].dt.month

        #print(df['Year'])

        grouped_df = df.groupby(['Year','Month','MeetingDate', 'GameName' ,'BetType']).sum()

        grouped_df.to_csv(directory+namefile, sep=';', encoding='latin-1',decimal=',')

        
        
        
        
        
    start_date+=delta
    #break