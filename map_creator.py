# -*- coding: utf-8 -*-
"""
This file fits the shapefile county names to cleaned_press_directories
"""


from scripts.press_directories_cleaner import cleaned_press_directories




import geopandas as gpd
import numpy as np
import os
import pickle

pickle_file = "scripts/data/elections_replaced.pkl"
          
with open(pickle_file, 'rb') as f:
    elections_replaced = pickle.load(f)


map_geojson = gpd.read_file("geodata/UKDefinitionA.json")
map_geojson["press_county"] = map_geojson["NAME"].str.lower()

press_column = {
    "angus" : "forfarshire",
    "antrim" : "antrim county",
    "armagh" : "armagh county",
    "brecknockshire" : "breconshire",
    "caernarfonshire" : "carnarvonshire",
    "anglesey" : "isle of anglesey",
    "buteshire" : "isle of bute",
    "devon" : "devonshire",
    "down" : "down county",
    "dunbartonshire" : "dumbartonshire",
    "east lothian" : "haddingtonshire",
    "fermanagh" : "fermanagh county",
    "glamorgan" : "glamorganshire",
    "londonderry" : "londonderry county",
    "shetland" : "shetland isles",
    "somerset" : "somersetshire",
    "tyrone" : "tyrone county",
    "west lothian" : "linlithgowshire"
    
}


map_geojson["press_county"] = map_geojson["press_county"].replace(press_column)


counties_map = map_geojson["press_county"].tolist()

counties_press = list(cleaned_press_directories["county"].unique())

counties_press.sort()

counties_elections = list(elections_replaced["cst_n"].unique())

only_press = np.setdiff1d(counties_press, counties_map).tolist()

only_map = np.setdiff1d(counties_map, counties_press).tolist()

map_geojson.to_file('geodata/updated_map.json', driver='GeoJSON')



