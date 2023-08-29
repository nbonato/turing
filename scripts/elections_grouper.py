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
import json
import pickle
from geocoding import changes
from shapely.geometry import shape, Point
import pandas as pd

with open("elections_cleaned.pkl", 'rb') as f:
    elections_replaced = pickle.load(f)
    
column_names = ["ignore", "place", "location", "confidence"]


coordinates = pd.read_csv("coordinat.csv", header = None, sep= ";", names = column_names)

coordinates[['latitude', 'longitude']] = coordinates['location'].str.split(',', expand=True).astype(float)
coordinates = coordinates.drop("ignore", axis=1)

with open('C:/Users/Nico/github/turing/geodata/updated_map.json', 'r') as f:
    js = json.load(f)



for feature in js['features']:

    polygon = shape(feature['geometry'])
    
    for index, row in coordinates.iterrows():
        point = Point(row["longitude"], row["latitude"])
        
        if polygon.contains(point):
            coordinates.at[index, "county"] = feature["properties"]["NAME"]
            #print ('Found containing polygon:', feature["properties"]["NAME"])
           
            
county_mapping = dict(zip(coordinates['place'], coordinates['county'])) 
          
manual_correspondences = {
    "krikcaldy" : "Fife",
    "carow": "Eire",
    "cirenchester": "Gloucestershire",
    "cornwall, st austell": "Cornwall",
    "cornwall, st ives": "Cornwall",
    "denbigshire": "Denbighshire",
    "drogheda": "Eire",
    "edinburghshire": "Midlothian",
    "essex, harwich": "Essex",
    "glasgow, backfriars and hutcheson": "Lanarkshire",
    "glasgow, camlachie": "Lanarkshire",
    "haddingtonshire": "East Lothian",
    "harwich": "Essex",
    "kilkenny city": "Eire",
    "liverpool, scotland": "Lancashire",
    "monaghan county": "Eire",
    "montrose": "Angus",
    "rutlandshire": "Rutland",
    "st andrews": "Fife",
    "st. andrews": "Fife",
    "st. ives": "Cornwall",
    "the hartlepools": "Durham"
}
  


for key, value in manual_correspondences.items():
    county_mapping[key] = value



# file = open("pickles/elections_cleaned.pkl", 'rb')

# elections = pickle.load(file)

elections = elections_replaced


# 1910 had two elections in the course of the year, each with its
# # own ID: 636, 637
elections = elections[elections["id"] != 637]

# # In 1900 there are some inconsistencies in the data, maybe errors
# elections = elections[elections["yr"] != 1900]

# # need to clarify
# elections = elections[elections["yr"] != 1922]

# # need to clarify
# elections = elections[elections["yr"] != 1885]

# # need to clarify
# elections = elections[elections["yr"] != 1874]

# ISSUES ABOVE TO BE SCRUTINISED WITH CODE FOR GROUPED_DF

# THIS PART BELOW UNEARTHS SOME ISSUES WITH THE ELECTION DATA

# grousped_df = elections.groupby(
#     ['yr', 'cst', 'pty']
#     ).agg({'pev1': process_unique, 'pvs1': process_unique}
#     ).reset_index()
     

def process_unique(x):
    unique_values = x.unique()
    if len(unique_values) > 1:
        print("Multiple unique values found at index: cst={}, yr={}, index={}".format(x.name[0], x.name[1], x.index))
    return unique_values.tolist() if len(unique_values) > 1 else unique_values[0]


# Define a mapping function
def map_county(cst_n):
    try:
        return county_mapping[changes[cst_n]]
    except:
        print("unfound", cst_n)

elections["geolocated_county"] = elections['cst_n'].apply(map_county)



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
    



elections.to_csv("elections_geolocated.csv")

first = elections[elections["id"] == 622]    

# This part calculates the elected MP for each constituency and their party
# It does so by:
# 1. Taking all rows related to a constituency
# 2. Checking the number of seats up for election (variable mag)
# 3. Checking if the election was uncontested (variable vot1 == -992)

mps = {}
results = {}
results_copy = {}

for year in elections["yr"].unique():
    first = elections[elections["yr"] == year]    
    
    results_election = {}
    
    for constituency in first["cst_n"].unique():
        results_election[constituency] = {}
        constituency_df = first[first["cst_n"] == constituency]
        seats = constituency_df["mag"].unique()
        uncontested = constituency_df["vot1"].unique()
    #    for index, row in first[first["cst_n"] == constituency].iterrows():
        # Check if those values are not unique, if they aren't, that's a problem
    
        try:
            seats = int(seats)
        except:
            print("ERROR, seats is not an integer", seats, constituency, year)
        
        try:
            uncontested = int(uncontested)
        except:
            print("ERROR, uncontested is not an integer", uncontested, constituency, year)
            continue
        
        # should be pty
        parties = constituency_df["pty_n"].unique()
        parties_running = len(parties)

        if seats == 1:
            if uncontested == -992:
                # This means that the elections is uncontested with a single seat
                if parties_running > 1:
                    print("ERROR, there are multiple parties running for one seat")
        
        if uncontested == -992:
            # This means that the elections is uncontested
            if parties_running > seats:
                # This would be an error, since it cannot be uncontested if there
                # are more parties than seats, in principle
                print("ERROR, there are more parties than seats in uncontested election", constituency, year)
            
            else:
                # Mostly used for 3 or 4 seats constituencies where there might be fewer
                # parties than seats and one party is gettint multiple seats
                for party in constituency_df["pty_n"]: 
                    
                    if party in results_election[constituency].keys():
                        results_election[constituency][party] += int(seats/len(constituency_df["pty_n"]))
                        #print(constituency, party, results_first[constituency])
    
                    else:
                        results_election[constituency][party] = int(seats/len(constituency_df["pty_n"]))
                #print(constituency, party, results_first[constituency])
        
        else:
            if parties_running == 1:
                results_election[constituency][parties[0]] = int(seats)
            elif parties_running > 1:
                sorted_constituency_df = constituency_df.sort_values("cvs1", ascending=False)
                # Get the first three lines of the dataframe
                df = sorted_constituency_df.iloc[0:3]
                
                # Group the dataframe by column pty
                grouped_df = df.groupby("pty_n")
                
                # Get the frequency counts of each party
                party_counts = grouped_df["pty_n"].size()
                
                # Create a dictionary with the party names and their frequency counts
                party_dict = dict(zip(party_counts.index, party_counts))
                results_election[constituency] = party_dict 
            else:
                print("ERROR, there are 0 or less parties running")
        if seats < 0:
            print(constituency)
        else:     
            if year in mps.keys():
                mps[year] += seats
            else:
                mps[year] = seats
    results[int(year)] = results_election
    results_copy[int(year)] = results_election
        #print(constituency, parties_running, seats)



yorkshire_cities = {key: value for key, value in county_mapping.items() if value == "Yorkshire"}
nan_values = {key: value for key, value in county_mapping.items() if type(value) == float}

for year_key, results_election in results.items():    
    test_dictionary = {}
    
    for ungrouped_constituency in results_election:

        geoloc_county = map_county(ungrouped_constituency)
        if type(geoloc_county) == str:
            geoloc_county = geoloc_county.lower()
        """ print(year, ungrouped_constituency, geoloc_county)
        if geoloc_county != "Aberdeenshire":
            break """
        if geoloc_county in test_dictionary.keys():
            # print(ungrouped_constituency, test_dictionary[geoloc_county])
            for key, value in results_election[ungrouped_constituency].items():
                
                if key in test_dictionary[geoloc_county].keys():
    
                    test_dictionary[geoloc_county][key] += value
                else:
                    #print(ungrouped_constituency, geoloc_county, key,  "not in keys")
    
                    test_dictionary[geoloc_county][key] = value
        else:
            # print(ungrouped_constituency, results_election[ungrouped_constituency])
    
            test_dictionary[geoloc_county] = results_election[ungrouped_constituency]

        
    results[year_key] = test_dictionary



# converted_data = {}
# for year, counties in results.items():
#     converted_data[year] = {}
#     for county, parties in counties.items():
#         converted_data[year][county] = {
#             "labels": [county],
#             "datasets": []
#         }
#         for party, value in parties.items():
#             converted_data[year][county]["datasets"].append({
#                 "label": party,
#                 "data": [value]
#             })
    
    
# nested_dict = {}

# for _, row in grousped_df.iterrows():
#     yr = int(row['yr'])
#     #cst = row['cst']
#     cst = counties_equivalence[yr][row['cst']]
#     pty = parties_equivalence[yr][row['pty']]
#     pvs1 = row['pvs1']
#     if pvs1 == -992:
#         pvs1 = "uncontested"

#     nested_dict.setdefault(yr, {})
#     nested_dict[yr].setdefault(cst, {})
#     nested_dict[yr][cst][pty] = pvs1
    
with open("elections.json", "w") as json_file:
    json.dump(results, json_file, indent = 2)
