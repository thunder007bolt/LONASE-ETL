#!/usr/bin/env python
# coding: utf-8

# In[19]:

while True:
        
    import pause
    from datetime import  date,datetime,timedelta
    delta = timedelta(days=1)
    #import datetime
    import pandas as pd
    import pause
    
    
    
    #print(date.today()+delta)
    
    #break
    

    #nextday = datetime.strptime((date.today()+delta).strftime('%Y%m%d'), '%Y%m%d').replace(hour=9, minute=0, second=0, microsecond=0)

    #pause.until(nextday)

    
    #end_date = datetime.date.today()#-5*delta
    end_date = date.today()#-5*delta
    currentYear = end_date.strftime("%Y")
    currentDay = end_date.strftime("%d/%m/%y")
    print(currentDay)
    
    print(datetime.now())
    
    
    # In[20]:
    
    
    def query_vente(opt):
        
        if 'sql'.lower() in str(opt).lower():
            opt = f""" < cast('{currentDay}' as date) """
            temp= f"""  DWHPR_TEMP.OPTIWARETEMP.SRC_PRD_VERIFICATION """
        elif 'oracle'.lower() in str(opt).lower():
            opt = f""" < TO_DATE('{currentDay}', 'DD/MM/YY') """
            temp= f""" OPTIWARETEMP.SRC_PRD_VERIFICATION """
        return f"""
   
    select V.NOMSYSTEME, V.LIBELLEJEUX,sum(coalesce(montant,0))-sum(coalesce(montant_annule,0)) as ca ,te.jour
    from {temp} V
    cross join USER_DWHPR.DIM_TEMPS Te
    left join user_dwhpr.FAIT_VENTE F on Te.idtemps = f.idtemps and V.IDTERMINAL = f.IDTERMINAL
    where te.anneec = '{currentYear}' 
    and te.jour {opt}
    group by te.jour,V.NOMSYSTEME , V.LIBELLEJEUX
    order by te.jour,V.NOMSYSTEME , V.LIBELLEJEUX
    
    """
    
    
    # In[21]:
    
    
    def query_lots(opt):
        if 'sql'.lower() in str(opt).lower():
            opt = f""" < cast('{currentDay}' as date) """
            temp= f"""  DWHPR_TEMP.OPTIWARETEMP.SRC_PRD_VERIFICATION """

        elif 'oracle'.lower() in str(opt).lower():
            opt = f""" < TO_DATE('{currentDay}', 'DD/MM/YY') """
            temp= f""" OPTIWARETEMP.SRC_PRD_VERIFICATION """

        return f"""
    
    select V.NOMSYSTEME , V.LIBELLEJEUX,
    sum(coalesce(montant,0))-sum(coalesce(montant_annule,0)) as ca ,
    sum(coalesce(paiements,0)) as lot,
    te.jour
    from {temp} V cross join USER_DWHPR.DIM_TEMPS Te
    left join user_dwhpr.FAIT_LOTS F on Te.idtemps = f.idtemps and V.IDTERMINAL = f.IDTERMINAL
    where te.anneec = '{currentYear}' 
    and te.jour {opt}
    group by te.jour,V.NOMSYSTEME , V.LIBELLEJEUX
    order by te.jour,V.NOMSYSTEME , V.LIBELLEJEUX
    
    """
    
    
    # In[22]:
    
    
    import cx_Oracle
    
    username = 'USER_DWHPR'
    password = 'optiware2016'
    
    #dsn = '192.168.1.237/OPTIWARE_TEMP'
    dsn = cx_Oracle.makedsn('192.168.1.237', 1521, service_name='DWHPR')
    port = 1521
    encoding = 'UTF-8'
    
    try:
        cx_Oracle.init_oracle_client(lib_dir=r"C:\instantclient_21_6")
    except:
        print("La base de donnee a deja ete initialisee")
    
    conn1 = cx_Oracle.connect(username,password,dsn)
    cur1 = conn1.cursor() #creates a cursor object
    
    
    # SQL query
    # Execute query and load data into DataFrame
    df_oralce_vente = pd.read_sql(query_vente('oracle'), con=conn1)
    df_oralce_vente.columns = ['nomsysteme', 'libellejeux','ca_oracle', 'jour']
    
    
    # In[ ]:
    
    
    df_oracle_lots = pd.read_sql(query_lots('oracle'), con=conn1)
    df_oracle_lots.columns = ['nomsysteme', 'libellejeux', 'ca_oracle','lot_oracle','jour']
    #print(df)
    
    
    # In[ ]:
    
    
    
    
    
    # In[ ]:
    
    
    import pyodbc
    SERVER = 'SRVSQLDWHPRD'
    DATABASE = 'DWHPR'
    USERNAME = 'USER_DWHPR'
    PASSWORD = 'optiware2016'
    connectionString = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SERVER};DATABASE={DATABASE};UID={USERNAME};PWD={PASSWORD}'
    conn2 = pyodbc.connect(connectionString)
    cursor2 = conn2.cursor()
    
    # SQL query
    
    # Execute query and load data into DataFrame
    df_sqlserver_vente = pd.read_sql_query(query_vente('sql'), conn2)
    df_sqlserver_vente.columns = ['nomsysteme', 'libellejeux','ca_sqlserver', 'jour']
    df_sqlserver_lots = pd.read_sql_query(query_lots('sql'), conn2)
    df_sqlserver_lots.columns = ['nomsysteme', 'libellejeux', 'ca_sqlserver','lot_sqlserver','jour']
    
    
    # In[ ]:
    
    
    
    
    
    # In[ ]:
    
    
    #print(df2['ca']-df['ca'])
    
    merged_vente = pd.merge(df_oralce_vente, df_sqlserver_vente, on=['nomsysteme', 'libellejeux', 'jour'], suffixes=('_df1', '_df2'))
    merged_lots = pd.merge(df_oracle_lots, df_sqlserver_lots, on=['nomsysteme', 'libellejeux', 'jour'], suffixes=('_df1', '_df2'))
    
    #print(merged_df)
    # Subtract the 'Salary' columns from both DataFrames
    merged_vente['ca_oracle_minus_sqlserver'] = merged_vente['ca_oracle'] - merged_vente['ca_sqlserver']
    
    merged_lots['ca_oracle_minus_sqlserver'] = merged_lots['ca_oracle'] - merged_lots['ca_sqlserver']
    merged_lots['lot_oracle_minus_sqlserver'] = merged_lots['lot_oracle'] - merged_lots['lot_sqlserver']
    
    df1 = merged_vente[ (merged_vente['ca_oracle_minus_sqlserver'] >= 1.0) | (merged_vente['ca_oracle_minus_sqlserver'] <= -1.0)] #(merged_vente['ca_oracle_minus_sqlserver'] != 0.0) &
    df2 = merged_lots[ (merged_lots['ca_oracle_minus_sqlserver'] >= 1.0) | (merged_lots['ca_oracle_minus_sqlserver'] <= -1.0) | (merged_lots['lot_oracle_minus_sqlserver'] >= 1.0) | (merged_lots['lot_oracle_minus_sqlserver'] <= -1.0)]
    
    df3 = merged_vente[ (merged_vente['ca_oracle'] == 0.0) | (merged_vente['ca_sqlserver'] == 0.0)]
    df4 = merged_lots[ (merged_lots['ca_oracle'] == 0.0) | (merged_lots['ca_sqlserver'] == 0.0) | (merged_lots['lot_sqlserver'] == 0.0) | (merged_lots['lot_oracle'] == 0.0)]
    
    filename = r"K:\DATA_FICHIERS\VIRTUEL_EDITEC\sqlVSoracle_"+str(datetime.now()).replace('.','_').replace(':','_')+".xlsx"

    print(datetime.now())
    
    print("le rapport a bien ete genere")
    
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        df1.to_excel(writer, sheet_name='dif_ca', index=False)
        df2.to_excel(writer, sheet_name='dif_lots', index=False)
        df3.to_excel(writer, sheet_name='ca_vide', index=False)
        df4.to_excel(writer, sheet_name='ca_lot_vide', index=False)
    
    #newdf = merged_df[(merged_df['ca_diff'] != 1.0) & (merged_df['ca_diff'] >= 1.0) | (merged_df['ca_diff'] <= -1.0)]
    #print( newdf )
    
    #newdf.to_csv(r"K:\DATA_FICHIERS\VIRTUEL_EDITEC\sqlVSoracle.csv",sep=';',index=False)
    
    
    # In[ ]:
    
    
    #print(df_sqlserver_vente)
    
    
    # In[ ]:
    
    
    cur1.close()
    conn1.close()  
    
    
    # In[ ]:
    
    
    cursor2.close()
    conn2.close()  
    
    import gc

    gc.collect()

    #You'll need to check for user-defined variables in the directory
    #for obj in d:
    for obj in dir():
        #checking for built-in variables/functions
        if not obj.startswith('__'):
            #deleting the said obj, since a user-defined function
            del globals()[obj]    
    
    # In[ ]:
    
    
    break
    
    
    
    
    
    # In[ ]:
    
    
    
    
    
    # In[ ]:
    
    
    
    
