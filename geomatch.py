import json
from shapely.geometry import shape, GeometryCollection, Point
import pandas as pd


column_names = ["ignore", "place", "location", "confidence"]
coordinates = pd.read_csv("scripts/coordinates5.csv", header = None, sep= ";", names = column_names)
coordinates[['latitude', 'longitude']] = coordinates['location'].str.split(',', expand=True).astype(float)
coordinates = coordinates.drop("ignore", axis=1)






with open('geodata/updated_map.json', 'r') as f:
    js = json.load(f)



point = Point(-2.099075, 57.149651)


a = 0
for feature in js['features']:

    polygon = shape(feature['geometry'])
    
    for index, row in coordinates.iterrows():
        point = Point(row["longitude"], row["latitude"])
        
        if polygon.contains(point):
            coordinates.at[index, "county"] = feature["properties"]["NAME"]
            #print ('Found containing polygon:', feature["properties"]["NAME"])
           
            
county_mapping = dict(zip(coordinates['place'], coordinates['county']))  

manual_correspondences = {
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

