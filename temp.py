print("\n extract_Mini_Shop \n")
exec(open("C:\ETL\Base\extract_Mini_Shop.py").read())

import subprocess

print("\n extract_virtuelAmabel - Pivot_detail \n")
subprocess.Popen(['python', "C:\ETL\Base\extract_virtuelAmabel - Pivot_detail.py"],
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)

print("\n extract_gitech - PHYSIQUE \n")
subprocess.Popen(['python', "C:\ETL\Base\extract_gitech - PHYSIQUE.py"],
                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)




"""
ECART PARIFOOT ONLINE
PMU SENEGAL ( VERIFICATION DES FICHIERS EXTRAITS )
PMU LOT VERIFICATION A FAIRE ( DESACTIVE )
"""