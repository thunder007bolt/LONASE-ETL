import cx_Oracle
import pandas as pd
import numpy as np
import datetime # Pour pd.to_datetime

def LoadUSSDData(generalDirectory, start_date, conn, cur):
    """
    Charge les données USSD depuis un fichier CSV dans une table temporaire Oracle.
    Retourne True si le chargement est réussi, False sinon.
    """
    directory = generalDirectory + r"USSD\\"
    file_pattern = directory + f"**\\GFM_CDR_DETAILS_{str(start_date)}.csv"
    files = glob.glob(file_pattern, recursive=True)

    print(f"Recherche de fichiers USSD: {file_pattern}, Trouvés: {len(files)}")

    if not files:
        print(f"Le fichier USSD du {start_date} n'a pas ete extrait ")
        return False

    file_path = files[0]
    try:
        data = pd.read_csv(file_path, sep=';', index_col=False, dtype=str)
        # Conversion des dates avec gestion des erreurs
        data['Jour'] = pd.to_datetime(data['Jour'], errors='coerce').dt.strftime('%d/%m/%Y')
        data['Date Appel'] = pd.to_datetime(data['Date Appel'], errors='coerce').dt.strftime('%d/%m/%Y %H:%M')

        data = pd.DataFrame(data, columns=['Date Appel', 'Jour', 'Numéro Serveur', 'Numéro Appelant', 'Durée Appel',
                                           'Total Appels', 'Total CA'])
        data = data.replace(np.nan, '') # Remplacer NaN par des chaînes vides après conversion
        data_list = list(data.to_records(index=False))

        # Vider la table temporaire avant d'insérer de nouvelles données
        cur.execute("truncate table optiwaretemp.TEMP_USSD_IVR")
        conn.commit()

        cur.executemany(
            """INSERT INTO optiwaretemp.TEMP_USSD_IVR("DATEAPPEL","JOUR","NUMEROSERVEUR","NUMEROAPPELANT","DUREEAPPEL","TOTALAPPELS","TOTALCA") VALUES(:1, :2, :3, :4, :5, :6, :7)""",
            data_list)
        conn.commit()
        print(f"Données USSD chargées depuis {file_path}")
        return True
    except Exception as e:
        print(f"Erreur lors du chargement du fichier USSD {file_path}: {e}")
        return False

def ChargeUSSD(debut, fin, conn, cur):
    """
    Traite les données USSD chargées dans la table temporaire TEMP_USSD_IVR
    pour mettre à jour les tables FAIT_VENTE, FAIT_LOTS, DTM_CA_DAILY, DTM_CA et AR_USSD_IVR.
    """
    print("################# DEBUT INSERT USSD ############")
    # Terminaux
    cur.execute(f"""
    INSERT INTO USER_DWHPR.DIM_TERMINAL(IDCCS,OPERATEUR,STATUT,IDSYSTEME)
    SELECT  389 IDCCS, OPERATEUR, '' STATUT, 175 IDSYSTEME
        FROM (
                   SELECT DISTINCT NumeroServeur OPERATEUR
                    FROM OPTIWARETEMP.TEMP_USSD_IVR
                   WHERE NumeroServeur NOT IN (SELECT OPERATEUR FROM USER_DWHPR.DIM_TERMINAL WHERE IDSYSTEME=175)
             ) S
    """) # Removed GROUP BY et DIM_CCS car IDCCS est fixe
    conn.commit()

    # Suppression fait_vente et fait_lots
    cur.execute(f""" delete from user_dwhpr.fait_vente
    WHERE IDJEUX = 471
    AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 175)
    AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
    """)
    conn.commit()
    cur.execute(f"""delete from user_dwhpr.fait_lots
    WHERE IDJEUX = 471
    AND IDTERMINAL in (select idterminal from user_dwhpr.dim_terminal where idsysteme = 175)
    AND idtemps IN (select idtemps from user_dwhpr.dim_temps where jour between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}' )
    """)
    conn.commit()

    # Insertion FAIT_VENTE
    cur.execute(f"""
    INSERT INTO USER_DWHPR.FAIT_VENTE(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,TICKET_EMIS,TICKET_ANNULE,ANNEE,MOIS,JOUR)
    SELECT  7181 IDVENDEUR,
        T.IDTERMINAL,
		Te.IDTEMPS,
	    471 IDJEUX,
		MONTANT,
		0 MONTANT_ANNULE,
       '' TICKET_EMIS,
		'' TICKET_ANNULE,
		TO_CHAR(Te.JOUR,'YYYY') ANNEE,
         TO_CHAR(Te.JOUR,'MM') MOIS,
         Te.JOUR
        FROM (
	         select NumeroServeur as Operateur , TO_DATE(JOUR,'dd/mm/yyyy') JOUR, TO_NUMBER(trim(REPLACE(REPLACE(TOTALCA,'.',','),' ',''))) Montant
		    FROM OPTIWARETEMP.TEMP_USSD_IVR
         ) F, USER_DWHPR.DIM_TERMINAL T, USER_DWHPR.DIM_TEMPS Te
    WHERE T.OPERATEUR = F.OPERATEUR
    AND T.IDSYSTEME=175
    AND TO_DATE(Te.JOUR,'dd/mm/yy')=F.JOUR
    """)
    conn.commit()

    # Insertion FAIT_LOTS
    cur.execute(f"""
    INSERT INTO USER_DWHPR.FAIT_LOTS(IDVENDEUR,IDTERMINAL,IDTEMPS,IDJEUX,MONTANT,MONTANT_ANNULE,PAIEMENTS,ANNEE,MOIS,JOUR)
    SELECT  7181 IDVENDEUR, T.IDTERMINAL, Te.IDTEMPS,
        471 IDJEUX, MONTANT, 0 MONTANT_ANNULE,
        0  PAIEMENTS,
		TO_CHAR(Te.JOUR,'YYYY') ANNEE,
         TO_CHAR(Te.JOUR,'MM') MOIS,
         Te.JOUR
    FROM (
	     select NumeroServeur as Operateur , TO_DATE(JOUR,'dd/mm/yyyy') JOUR, TO_NUMBER(trim(REPLACE(REPLACE(TOTALCA,'.',','),' ',''))) Montant
		 FROM OPTIWARETEMP.TEMP_USSD_IVR
         ) F, USER_DWHPR.DIM_TERMINAL T, USER_DWHPR.DIM_TEMPS Te
    WHERE  upper(trim(T.OPERATEUR ))= upper(trim(F.OPERATEUR))
    AND T.IDSYSTEME=175
    AND TO_DATE(Te.JOUR,'dd/mm/yy')=F.JOUR
    """)
    conn.commit()

    # DTM_CA_DAILY
    cur.execute(f"""
    MERGE INTO user_dwhpr.dtm_ca_daily t
    USING (
       SELECT Te.ANNEEC AS ANNEE,
              Te.MOISC AS MOIS,
              Te.JOUR,
              SUM(NVL(F.MONTANT, 0)) - SUM(NVL(F.MONTANT_ANNULE, 0)) AS CA_USSD
         FROM user_dwhpr.FAIT_VENTE F
         JOIN user_dwhpr.DIM_TERMINAL T ON F.idterminal = T.idterminal
         JOIN user_dwhpr.DIM_TEMPS Te ON Te.IDTEMPS = F.IDTEMPS
         JOIN user_dwhpr.DIM_JEUX J ON F.IDJEUX = J.IDJEUX
         WHERE Te.JOUR between '{str(debut.strftime('%d/%m/%Y'))}' and '{str(fin.strftime('%d/%m/%Y'))}'
          AND F.IDJEUX = 471
          AND T.IDSYSTEME = 175
        GROUP BY Te.ANNEEC, Te.MOISC, Te.JOUR
    ) g
    ON (t.annee = g.annee AND t.mois = g.mois AND t.jour = g.jour)
    WHEN MATCHED THEN UPDATE SET t.CA_USSD = g.CA_USSD
    """)
    conn.commit()

    # DTM_CA (mensuel)
    cur.execute(f"""
    MERGE INTO user_dwhpr.dtm_ca t
    USING (
       SELECT F.ANNEE AS ANNEE,
              F.MOIS AS MOIS,
              SUM(NVL(F.MONTANT, 0)) - SUM(NVL(F.MONTANT_ANNULE, 0)) AS CA_USSD
         FROM user_dwhpr.FAIT_VENTE F
         JOIN user_dwhpr.DIM_TERMINAL T ON F.idterminal = T.idterminal
         JOIN user_dwhpr.DIM_TEMPS Te ON Te.IDTEMPS = F.IDTEMPS
         JOIN user_dwhpr.DIM_JEUX J ON F.IDJEUX = J.IDJEUX
        WHERE Te.ANNEEC = '{str(debut.year)}' AND Te.MOISC = '{str(debut.month).zfill(2)}'
          AND F.IDJEUX = 471
          AND T.IDSYSTEME = 175
        GROUP BY F.ANNEE, F.MOIS
     ) g
     ON (t.annee = g.annee AND t.mois = g.mois)
     WHEN MATCHED THEN UPDATE SET t.CA_USSD = g.CA_USSD
    """)
    conn.commit()

    # Archivage
    cur.execute(f"""
        delete from OPTIWARETEMP.AR_USSD_IVR
      where jour in (select distinct jour from OPTIWARETEMP.TEMP_USSD_IVR)
    """)
    conn.commit()
    cur.execute(f"""
        insert into OPTIWARETEMP.AR_USSD_IVR
        select *  from OPTIWARETEMP.TEMP_USSD_IVR
    """)
    conn.commit()

    print("La procedure d'insertion USSD s'est bien deroulee")
    cur.execute("""truncate table optiwaretemp.TEMP_USSD_IVR""")
    conn.commit()
    print("################# FIN INSERT USSD ############")

# Nécessite glob pour la fonction LoadUSSDData
import glob
