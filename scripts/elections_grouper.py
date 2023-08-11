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

from elections import elections_replaced

# file = open("pickles/elections_cleaned.pkl", 'rb')

# elections = pickle.load(file)

elections = elections_replaced


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




# grouped_df = elections.groupby(
#     ['yr', 'cst', 'pty']
#     ).agg({'pev1': process_unique, 'pvs1': process_unique}
#     ).reset_index()
     

# Dictionary that stores the county corresponding to a specific county id per
# each year
counties_equivalence = {}
for _, row in elections.iterrows():
    yr = row['yr']
    cst = row['cst']
    cst_n = row['cst_n']

    counties_equivalence.setdefault(yr, {})
    counties_equivalence[yr][cst] = cst_n
    

# Dictionary that stores the party corresponding to a specific party id per
# each year
parties_equivalence = {}
for _, row in elections.iterrows():
    yr = row['yr']
    pty = row['pty']
    pty_n = row['pty_n']

    parties_equivalence.setdefault(yr, {})
    parties_equivalence[yr][pty] = pty_n
    

first = elections[elections["id"] == 622]    

# This part calculates the elected MP for each constituency and their party
# It does so by:
# 1. Taking all rows related to a constituency
# 2. Checking the number of seats up for election (variable mag)
# 3. Checking if the election was uncontested (variable vot1 == -992)

results_first = {}
for constituency in first["cst_n"].unique():
    results_first[constituency] = {}
    constituency_df = first[first["cst_n"] == constituency]
    seats = constituency_df["mag"].unique()
    uncontested = constituency_df["vot1"].unique()
#    for index, row in first[first["cst_n"] == constituency].iterrows():
    # Check if those values are not unique, if they aren't, that's a problem

    try:
        seats = int(seats)
    except:
        print("ERROR")
    
    try:
        uncontested = int(uncontested)
    except:
        print("ERROR")
    
    # should be pty
    parties = constituency_df["pty_n"].unique()
    parties_running = len(parties)

    if seats == 1:
        if uncontested == -992:
            # This means that the elections is uncontested with a single seat
            if parties_running > 1:
                print("error")
    
    if uncontested == -992:
        # This means that the elections is uncontested
        if parties_running > seats:
            # This would be an error, since it cannot be uncontested if there
            # are more parties than seats, in principle
            print("ERROR")
        
        else:
            # Mostly used for 3 or 4 seats constituencies where there might be fewer
            # parties than seats and one party is gettint multiple seats
            for party in constituency_df["pty_n"]: 
                
                if party in results_first[constituency].keys():
                    results_first[constituency][party] += seats/len(constituency_df["pty_n"])
                    #print(constituency, party, results_first[constituency])

                else:
                    results_first[constituency][party] = seats/len(constituency_df["pty_n"])
            #print(constituency, party, results_first[constituency])
    
    else:
        if parties_running == 1:
            results_first[constituency][parties[0]] = seats
        elif parties_running > 1:
            constituency_df.sort_values("cvs1", inplace=True)

            print(constituency_df)
        else:
            print("ERROR")
            
    #print(constituency, parties_running, seats)

    
    
    
    
    
    
'''
nested_dict = {}

for _, row in grouped_df.iterrows():
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
    json.dump(nested_dict, json_file, indent = 2)
'''