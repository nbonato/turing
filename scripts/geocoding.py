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
timeout = 1


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


# Addresses to geocode
data = []

for index, row in locations.iterrows():
    data.append(f"{row['cst_n']}")
    

coordinates = []
start = 100

while start + 50 <= len(data)-1:
    coordinates.append(getLocations(data[start:start+50]))
    start += 50



locations_dict_list = []

for element in coordinates:
    locations_dictionary  = {}

    locations_dictionary["query"] = element["query"]["text"]
    try:
        locations_dictionary["searched"] = element["query"]["parsed"]["city"]
    except:
        print(locations_dictionary["query"], " not a city")
        try:
            locations_dictionary["searched_type"] = element["result_type"]
        except:
            locations_dictionary["found"] = "no"
    try:
        locations_dictionary["coordinates"] = f"{element['lat']}, {element['lon']}"
    except:
        pass
    try:
        locations_dictionary["confidence"] = element["rank"]["confidence"]
    except:
        pass
    locations_dict_list.append(locations_dictionary)


locations_dataframe = pd.DataFrame.from_dict(locations_dict_list)
locations_dataframe.to_csv("coordinates.csv",sep=";")