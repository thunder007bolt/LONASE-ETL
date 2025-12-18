import pandas as pd
import glob
import os



from datetime import date,timedelta #,datetime,timedelta
import datetime


delta = datetime.timedelta(days=1)
end_date = datetime.date.today()
start_date = end_date - delta

#print(start_date)
start_date = datetime.date(2024, 12, 17)
#end_date = start_date+delta
end_date = datetime.date(2024, 12, 18)

debut = start_date
fin = end_date-delta

# Répertoire contenant les fichiers CSV
directory_path  = r"K:\DATA_FICHIERS\HONORE_GAMING\\"
output_directory = r"K:\DATA_FICHIERS\MINI_SHOP\\"  # Dossier pour enregistrer les fichiers filtrés

# Assure que le répertoire de sortie existe
os.makedirs(output_directory, exist_ok=True)

                                         
  
    
# Parcourir tous les fichiers CSV dans le répertoire
file_list = glob.glob(directory_path+f"*\\daily-modified-horse-racing-tickets-detailed_{str(start_date).replace('-','')}.csv",recursive=True)
#file_list = glob.glob(os.path.join(directory_path, '*.csv')) 
print(len(file_list))
                      
jour=start_date -delta  
day = jour.strftime("%Y-%m-%d")                    
print(day)

for file_path in file_list:
    print(f"Traitement du fichier : {file_path}")
    # Charger le fichier CSV
    df = pd.read_csv(file_path,sep=';')
    df['MeetingDate'] = df['MeetingDate'].astype(str)
    df['MeetingDate'] = [str(i)[:10] for i in df['MeetingDate']]

    print(df['MeetingDate'][:10])

    print(df.dtypes)
    # Filtrer les lignes selon les conditions
    # Assure que 'ReportDateTime' et 'MeetingDate' sont bien des types datetime
    #df['ReportDateTime'] = pd.to_datetime(df['ReportDateTime'])
    #df['MeetingDate'] = pd.to_datetime(df['MeetingDate'])
   # print(df)
    #print(df['MeetingDate'])
   # print(df['ReportDateTime'])   
                 
                     
    # Filtrer les lignes selon les conditions
    #filtered_df = df[df['MeetingDate'].astype(str).str.contains(str(day)) ]
    filtered_df = df[df['MeetingDate'].str.contains(str(day)) ]
        #(df['TerminalDescription'].astype(str).str.contains("10961|38165|38166|38167|38168|38169"))
    
    #print(df['MeetingDate'] )
    print(filtered_df)
    #filtered_df = df[
     #           (df['MeetingDate'] == (df['ReportDateTime'] - pd.Timedelta(days=1)).astype(str)) &
      #          (df['TerminalDescription'].isin([10962, 38165,38166,38167,38168,38169]))
    #]                  

    # Vérifier si des données ont été filtrées
    #if not filtered_df.empty:
        # Générer un nom de fichier pour la sortie
       # output_file_path = os.path.join(output_directory, 
                    #os.path.basename(file_path).replace('.csv', '_filtered.csv')
       # )

        # Sauvegarder le fichier filtré
        #filtered_df.to_csv(output_file_path, index=False)
       # print(f"Fichier filtré sauvegardé : {output_file_path}")
   # else:
     #   print(f"Aucune donnée correspondante dans le fichier : {file_path}")
    
#print(start_date)
#start_date+=delta                    

   

#print("Traitement terminé.")