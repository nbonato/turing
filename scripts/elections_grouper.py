# -*- coding: utf-8 -*-
"""
This script groups together electoral data based on counties
The idea is to return the correct percentage of vote cast per each party
in a costituency or group of costituencies
elections_cleaner.py already takes care of cleaning the elections 
dataset to make each costituency match a county, so this script is not
concerned with that




Particular situations are highlighted here: https://www.notion.so/nbonato/Errors-in-Elections-03b5a4b48a31441d84d3c640a3457970
"""
import numpy as np
import pickle
import json

file = open("pickles/elections_cleaned.pkl", 'rb')

elections = pickle.load(file)



# 1910 had two elections in the course of the year, each with its
# own ID: 636, 637
elections = elections[elections["yr"] != 1910]

# In 1900 there are some inconsistencies in the data, maybe errors
elections = elections[elections["yr"] != 1900]

# need to clarify
elections = elections[elections["yr"] != 1922]

# need to clarify
elections = elections[elections["yr"] != 1885]

# need to clarify
elections = elections[elections["yr"] != 1874]




def process_unique(x):
    unique_values = x.unique()
    if len(unique_values) > 1:
        print("Multiple unique values found at index: cst={}, yr={}, index={}".format(x.name[0], x.name[1], x.index))
    return unique_values.tolist() if len(unique_values) > 1 else unique_values[0]




grouped_dict = elections.groupby(
    ['yr', 'cst', 'pty']
    ).agg({'pev1': process_unique, 'pvs1': process_unique}
    ).reset_index()
          
counties_equivalence = {}
for _, row in elections.iterrows():
    yr = row['yr']
    cst = row['cst']
    cst_n = row['cst_n']

    counties_equivalence.setdefault(yr, {})
    counties_equivalence[yr][cst] = cst_n
    
    
parties_equivalence = {}
for _, row in elections.iterrows():
    yr = row['yr']
    pty = row['pty']
    pty_n = row['pty_n']

    parties_equivalence.setdefault(yr, {})
    parties_equivalence[yr][pty] = pty_n
    
    
nested_dict = {}

for _, row in grouped_dict.iterrows():
    yr = int(row['yr'])
    #cst = row['cst']
    cst = counties_equivalence[yr][row['cst']]
    pty = parties_equivalence[yr][row['pty']]
    pvs1 = row['pvs1']
    if pvs1 == -992:
        pvs1 = "uncontested"

    nested_dict.setdefault(yr, {})
    nested_dict[yr].setdefault(cst, {})
    nested_dict[yr][cst][pty] = pvs1
    
with open("elections.json", "w") as json_file:
    json.dump(nested_dict, json_file)