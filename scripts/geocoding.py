# -*- coding: utf-8 -*-
"""
Created on Mon Aug  7 17:07:11 2023

@author: Nico
"""

import requests
import time
from combine import only_in_elections_cleaned
from elections import locations
import pandas as pd


locations["sub"] = locations["sub"].str.split("-", n=1).str[0]
locations["sub"] = locations["sub"].str.lstrip().str.rstrip()
# Keep only the unique rows.
locations = locations.drop_duplicates()


nation_replacements = {
    "wales and monmouthshire" : "wales"
    }

locations["sub"] = locations["sub"].replace(nation_replacements)

#

keep = ["scotland", "england", "wales",  "ireland", "northern ireland"]
locations = locations[locations["sub"].isin(keep)]

locations = locations[~locations["cst_n"].str.contains("university")]
nations = locations["sub"].unique()

apiKey = ""

# Open the file in read mode.
with open("APIKeys.txt", "r") as f:
    apiKey = f.read()
# With Batch Geocoding, you create a geocoding job by sending addresses and then, after some time, get geocoding results by job id
# You may require a few attempts to get results. Here is a timeout between the attempts - 1 sec. Increase the timeout for larger jobs.
timeout = 50


# Define circles used to bias search results to specific home nations
circles = {
    "scotland" : "56.998736,-4.556696,265825",
    "wales" : "52.430326,-3.540485,152977",
    "ireland" : "54.580670,-6.736986,96406", #just northern ireland
    "northern ireland" : "54.580670,-6.736986,96406", #just northern ireland,
    "england" : "52.410907,-2.378386,377497"
    }

# Limit the number of attempts
maxAttempt = 20
result = ""
def getLocations(places):
    url = "https://api.geoapify.com/v1/batch/geocode/search?filter=countrycode:gb&apiKey=" + apiKey
    response = requests.post(url, json = places)
    result = response.json()

    # The API returns the status code 202 to indicate that the job was accepted and pending
    status = response.status_code
    if (status != 202):
        print('Failed to create a job. Check if the input data is correct.')
        return
    jobId = result['id']
    getResultsUrl = url + '&id=' + jobId

    time.sleep(timeout)
    result = getLocationJobs(getResultsUrl, 0)
    if (result):
        print('You can also get results by the URL - ' + getResultsUrl)
        return result
    else:
        print('You exceeded the maximal number of attempts. Try to get results later. You can do this in a browser by the URL - ' + getResultsUrl)

def getLocationJobs(url, attemptCount):
    response = requests.get(url)
    result = response.json()
    status = response.status_code
    if (status == 200):
        print('The job is succeeded. Here are the results:')
        return result
    elif (attemptCount >= maxAttempt):
        return
    elif (status == 202):
        print('The job is pending...')
        time.sleep(timeout)
        return getLocationJobs(url, attemptCount + 1)



def replace_elements(list, dictionary):
  """Replaces elements from a list based on a dictionary.

  Args:
    list: The list to be modified.
    dictionary: A dictionary that maps old elements to new elements.

  Returns:
    The modified list.
  """

  for i in range(len(list)):
    if list[i] in dictionary:
      list[i] = dictionary[list[i]]

# Addresses to geocode
data = []




cardinal_points = ["north", "south", "centr", "east", "west", "mid"]
locations.sort_values("cst_n", inplace=True)

logs = {}
logs["cardinal location"] = []
logs["place in county"] = []
logs["district of"] = []
logs["parenthesis"] = []
logs["yorkshire"] = []

def clean(string):
    return string.rstrip().rstrip(",").lstrip()

for index, row in locations.iterrows():
# The log dictionary stores each change made in this process, to make it easier
# to check that there is no spillover of unwarranted changes
    place = clean(row['cst_n'])
    
    
    
# Many different spellings of Yorkshire subdivisions are in the dataset,
# making it difficult to intercept them with the other techniques without 
# overextending them to non-relevant cases
    if "yorkshire" in place:
        logs["yorkshire"].append({place : "yorkshire"})
        place = "yorkshire"

    if "(" in place:
        logs["parenthesis"].append({place : place.split("(")[0]})
        place = clean(place.split("(")[0])
    if "district of" in place:
        logs["district of"].append({place : place.split(" district of")[0]})
        place = clean(place.split(" district of")[0])
# The following lines check places with a comma in the name trying to understand
# whether they are subsets of a larger county, for example aberdeen, south being
# part of aberdeen or berkshire, newbury being part of berkshire
    if "," in place:
        original = place
        comma_split = place.split(",")
        for direction in cardinal_points:
            if direction in comma_split[1]:
                logs["cardinal location"].append({original : comma_split[0]})
                place = clean(comma_split[0])
                
                break
    if "," in place:
        comma_split = place.split(",")
        if "shire" in place.split(",")[0]:
            logs["place in county"].append({original : f"{comma_split[1]}, {comma_split[0]}"})
            place = clean(f"{comma_split[1]}, {comma_split[0]}")
    data.append(place)
    
typos = {
    "berwickshre": "berwickshire",
    "linconlnshire": "lincolnshire",
    "nuneatton, warwickshire": "nuneaton, warwickshire",
    "birminghman": "birmingham",
    "thrisk": "thrisk",
    "birminghman, edgbaston": "birmingham, edgbaston",
    "susex, lewes": "sussex, lewes",
    "krikcaldy": "kirkcaldy",
    "iverness-shire": "inverness-shire",
    "middlsex, spelthorne": "middlesex, spelthorne",
    "leicesterhsire, haborough": "leicestershire, haborough",
    "cirenchester": "cirenchester",
    "gloamorganshire": "glamorganshire",
    "durgavan": "dungarvan",
    "greenwhich": "greenwich",
    "prtsmouth": "portsmouth",
    "rowburghshire": "roxburghshire",
    "endinburghshire": "edinburghshire",
    "scaraborough": "scarborough",
    "surreey, kingston": "surrey, kingston",
    "liverppol": "liverpool",
    "sundersland": "sunderland",
    "esex, walthamstow": "essex, walthamstow",
    "clasgow, gorbals": "glasgow, gorbals",
    "kesington": "kensington",
    "kutsford, cheshire": "knutsford, cheshire",
    "norfold": "norfolk",
    "stafforshire": "staffordshire",
    "wighan": "wigan",
    "iverness": "inverness",
}
    
replace_elements(data, typos)
data = list(set(data))



start = 0

while start <= len(data)-1:
    coordinates = getLocations(data[start:start+50])
    start += 50
    locations_dict_list = []

    for element in coordinates:
        locations_dictionary  = {}

        locations_dictionary["query"] = element["query"]["text"]
        # try:
        #     locations_dictionary["searched"] = element["query"]["parsed"]["city"]
        # except:
        #     print(locations_dictionary["query"], " not a city")
        #     locations_dictionary["searched"] = element["query"]["text"]
        #     try:
        #         locations_dictionary["searched_type"] = element["result_type"]
        #         locations_dictionary["found"] = "yes"
        #     except:
        #         locations_dictionary["found"] = "no"
        try:
            locations_dictionary["coordinates"] = f"{element['lat']}, {element['lon']}"
        except:
            locations_dictionary["coordinates"] = ""
        try:
            locations_dictionary["confidence"] = element["rank"]["confidence"]
        except:
            locations_dictionary["confidence"] = ""
        locations_dict_list.append(locations_dictionary)


    locations_dataframe = pd.DataFrame.from_dict(locations_dict_list)
    locations_dataframe.to_csv("coordinates2.csv", mode="a", index=True, header=False, sep=";")

