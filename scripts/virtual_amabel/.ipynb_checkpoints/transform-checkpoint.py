import pandas as pd
import numpy as np
import win32com.client
import os
import re, time
from pathlib import Path
from base.logger import Logger
from utils.config_utils import get_config
import shutil

def get_configurations():
    config = get_config("gitech")
    extraction_dest_path = config["gitech"]["extraction_dest_relative_path"]
    data_path = config["paths"]["data_path"]
    transformation_dest_path = data_path + config["gitech"]["transformation_dest_relative_path"]
    destination_path = data_path + extraction_dest_path
    file_downloaded_name = config["gitech"]["file_downloaded_name"]
    destination_file = Path(destination_path + file_downloaded_name)
    logger = Logger(log_file="transformation_gitech.log").get_logger()

    return logger, transformation_dest_path, destination_file

def convert_xls_to_xlsx(path: Path) -> None:
    excel = win32com.client.gencache.EnsureDispatch('Excel.Application')
    wb = excel.Workbooks.Open(path.absolute())

    # FileFormat=51 is for .xlsx extension
    output = str(path.absolute().with_suffix(".xlsx"))
    wb.SaveAs(output, FileFormat=51)
    wb.Close()
    excel.Application.Quit()

def transform_csv_file():
    path, transformation_dest_path, logger = get_configurations()
    # Tous les fichiers du repertoire path seront traités
    # convert_xls_to_xlsx(path)
    # return
    # Supprimer le cache COM existant
    cache_path = os.path.join(os.environ["LOCALAPPDATA"], "Temp", "gen_py")
    shutil.rmtree(cache_path, ignore_errors=True)
    o = win32com.client.gencache.EnsureDispatch('Excel.Application')
    o.Visible = False

    #for path,dirs,files in os.walk(pth):
    for filename in os.listdir(str(path.absolute().parent)):
        print(filename)
        if "Etat de la course" in filename and filename.endswith('.xls'):
            #changer l'extension du fichier en xlsx
            # excel = win32com.client.gencache.EnsureDispatch('Excel.Application')
            # excel.Application.Quit()
            excel = win32com.client.gencache.EnsureDispatch('Excel.Application')
            wb = excel.Workbooks.Open(path.absolute())

            # FileFormat=51 is for .xlsx extension
            output = str(path.absolute().with_suffix(".xlsx"))
            wb.SaveAs(output, FileFormat=51)
            wb.Close()
            excel.Application.Quit()
            print("Fichier converti en xlsx")
            os.remove(str(path.absolute()))

            data = pd.read_excel(output,skiprows=range(1, 6))

            print(data.head())
            # recuperer la date dans le fichier
            dat1 = pd.read_excel(output) #,error_bad_lines=False
            date = dat1.iloc[1].str.replace("Date : Du:","").str.split(":")[0][0].replace("/","-").replace(" ","").replace("Au","")

            #print(date)

            # renommage des colonnes
            data.columns = ['No','Agences','Operateur','Vente','Annulation','Remboursement','Paiement','Resultat']

            # suppression de toutes les lignes comptenant Total et montant global
            data = data[data.Operateur != 'Total']
            data = data[data.Operateur != 'montant global']

            # suppression de la colonne No
            data = data.drop('No',axis=1)

            # insertion et remplissage de la colonne date suivant la date indiquée dans le fichier xls
            date_serie = pd.Series(np.random.randn(len(data)), index=data.index)
            data.insert(2, "Date vente",date_serie, True)
            data['Date vente'] = data['Date vente'].apply(lambda x: str(x).replace(str(x),str(date.replace("-","/"))))

            # remplissage de la colonne Agence, les valeurs nulles sont remplies par leurs agences correspondantes
            data = data.copy(deep=True)

            v_agence = data['Agences'].iloc[0]
            for i in range(0,len(data),1):
                #print(v_agence)
                if(pd.notnull(data['Agences'].iloc[i])):
                    v_agence = data['Agences'].iloc[i]
                else:
                    data['Agences'].iloc[i] = v_agence

            # Formattage des colonnes Vente, Annulation, Remboursement, Paiement, Resultat en numeric
            data['Resultat'] = data['Resultat'].map(lambda x: str(x).replace(u'\xa0',u''))
            data['Vente'] = data['Vente'].map(lambda x: str(x).replace(u'\xa0',u''))
            data['Annulation'] = data['Annulation'].map(lambda x: str(x).replace(u'\xa0',u''))
            data['Remboursement'] = data['Remboursement'].map(lambda x: str(x).replace(u'\xa0',u''))
            data['Paiement'] = data['Paiement'].map(lambda x: str(x).replace(u'\xa0',u''))
            data['Resultat'] = data['Resultat'].map(lambda x: str(x).rstrip('00').replace(',','') if(re.search(",",str(x))) else str(x) )
            data['Vente'] = data['Vente'].map(lambda x: str(x).rstrip('00').replace(',','') if(re.search(",",str(x))) else str(x) )
            data['Annulation'] = data['Annulation'].map(lambda x: str(x).rstrip('00').replace(',','') if(re.search(",",str(x))) else str(x) )
            data['Remboursement'] = data['Remboursement'].map(lambda x: str(x).rstrip('00').replace(',','') if(re.search(",",str(x))) else str(x) )
            data['Paiement'] = data['Paiement'].map(lambda x: str(x).rstrip('00').replace(',','') if(re.search(",",str(x))) else str(x) )

            data[['Vente','Annulation','Remboursement','Paiement','Resultat']] = data[['Vente','Annulation','Remboursement','Paiement','Resultat']].astype('int64')
            #print(data.head())
            #print(data.tail())
            #print(win32com.__gen_path__) C:\Users\hp\AppData\Local\Temp\gen_py\3.7
            namedfile = 'GITECH '+date.split('-')[2]+'-'+date.split('-')[1]+'-'+date.split('-')[0]+'.csv'

            if os.path.exists(str(path.absolute().parent)+namedfile):
                os.remove(path+namedfile)

            data.to_csv(transformation_dest_path+namedfile, index=False,sep=';',encoding='utf8')

            print(f"le fichier {namedfile} a bien ete transforme")

            # os.remove(path + filename.replace('.xls','.xlsx'))
    #print("tous les fichiers ont bien ete transformés")

if __name__ == '__main__':

    transform_csv_file(destination_file, transformation_dest_path, logger)

