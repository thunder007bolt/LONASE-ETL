# -*- coding: utf-8 -*-
"""
Created on Wed Mar 19 14:05:55 2025

@author: optiware3
"""

import pandas as pd
from itertools import combinations
import math

# Read the Excel file
# Replace 'data.xlsx' with your actual file name
df = pd.read_excel('K:\DATA_FICHIERS\VIRTUEL_EDITEC\Classeur1.xlsx')


try:
            
    df['MT_ENR'] = df['MT_ENR'].str.replace(',', '.').astype(float)
except:
    pass

try:

    df['MT_ANC'] = df['MT_ANC'].str.replace(',', '.').astype(float)
except:
    pass

#print(df['MT_ENR'])
#print(df['MT_ANC'])

#df = df.fillna(0)


#print(df.columns)

# Extract columns as lists
#column_a = df['MT_ENR'].tolist()  # e.g., [10, 20, 30]
#column_b = df['MT_ANC'].tolist()  # e.g., [5, 13, 6]

#column_a = [x for x in df['MT_ENR'].tolist() if x != 0 or x !='']
#column_b = [x for x in df['MT_ANC'].tolist() if x != 0 or x !='']

column_a = [x for x in df['MT_ENR'].tolist() if not (x == 0 or (isinstance(x, float) and math.isnan(x)))]
column_b = [x for x in df['MT_ANC'].tolist() if not (x == 0 or (isinstance(x, float) and math.isnan(x)))]

#print(column_a)

#print(column_b)

# Define the target result
target = 56166900#56139250  # Change this to your desired target

# Calculate sum of Column A
sum_a = sum(column_a)

# Generate all possible combinations of exclusions from Column B
found = False
for r in range(len(column_b) + 1):
    for excluded in combinations(column_b, r):
        remaining = [x for x in column_b if x not in excluded]
        sum_b_remaining = sum(remaining)
        result = sum_a - sum_b_remaining
        if result == target:
            print(f"Target {target} achieved by excluding {list(excluded)}")
            found = True
            break
    #if found:
        #break

if not found:
    print(f"No combination found that achieves target {target}")