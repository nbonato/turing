import pandas as pd
import time
import json 

from scripts.press_directories_cleaner import cleaned_press_directories
from map_creator import counties_map  



with open('geodata/updated_map.json', 'r') as f:
    js = json.load(f)





a = 0



# Start the timer
start_time = time.time()

cleaned_press_directories = cleaned_press_directories.sort_values("county")
counties = cleaned_press_directories["county"].unique()


# Only keep counties that are in the map
df = cleaned_press_directories[cleaned_press_directories['county'].isin(counties_map)]


df["S-POL"] = df["S-POL"].fillna("undefined")
#df = df.head(10000)

# def calculate_frequency(x):
#     frequency_dict = {}
#     for pol in x["S-POL"].unique():
#         count = x[x["S-POL"] == pol]["S-TITLE"].nunique()
#         frequency_dict[pol] = round(count / len(x) * 100, 2)
#     return frequency_dict

def calculate_frequency(x):
    frequency_dict = {}
    total_count = len(x)
    threshold = 5  # percentage threshold
    
    for pol in x["S-POL"].unique():
        count = x[x["S-POL"] == pol]["S-TITLE"].nunique()
        frequency = round(count / total_count * 100, 2)
        
        if frequency < threshold:
            # Group categories under 5% into "other"
            
            frequency_dict["other"] = frequency_dict.get("other", 0) + frequency
            frequency_dict["other"] = round(frequency, 2)

        else:
            frequency_dict[pol] = round(frequency, 2)
    # Sort the dictionary based on values in descending order
    frequency_dict = dict(sorted(frequency_dict.items(), key=lambda item: item[1], reverse=True))
    max_value = max(frequency_dict.values())
    max_keys = sorted([key for key, value in frequency_dict.items() if value == max_value])
    unspecified = ["undefined", "no-politics", "independent", "neutral"]

    if len(max_keys) == 1:
        majority = max_keys[0]
    else:
        if all(key in unspecified for key in max_keys):
            majority = "undefined"
        else:    
            # if len(max_keys) == 2:
            #     majority = f"{max_keys[0]} & {max_keys[1]}"
            # else:
            majority = "multiple majority"
    county_dict = {
        "press_data": frequency_dict,
        "majority": majority
        }
    return county_dict



frequency = (
    df.groupby(["year", "county"])
    .apply(calculate_frequency)
    .reset_index(name="results")
)



final_dict = frequency.groupby('year')[['county','results']].apply(lambda x: x.set_index('county')["results"].to_dict()).to_dict()



# Add a column for the combination of "county" and "year"
frequency["county_year"] = frequency["county"] + "_" + frequency["year"].astype(str)


positions = []
for year in final_dict:
    for county in final_dict[year]:

        positions.append(final_dict[year][county]["majority"])

positions_unique= set(positions)


def calculate_relative_frequency(data_list):
    total_items = len(data_list)
    unique_items = set(data_list)
    frequency_dict = {}

    for item in unique_items:
        frequency = data_list.count(item)
        frequency_dict[item] = frequency

    return frequency_dict

# Example list
data_list = positions

relative_frequencies = calculate_relative_frequency(data_list)

sorted_items = sorted(relative_frequencies.items(), key=lambda item: item[1], reverse=True)
most_common = [item[0] for item in sorted_items[:12]]

for year in final_dict:
    for county_data in final_dict[year]:
        if final_dict[year][county_data]["majority"] not in most_common:
            if "&" in final_dict[year][county_data]["majority"]:
                final_dict[year][county_data]["majority"] = "multiple majority"
            final_dict[year][county_data]["majority"] = "other"


# positions = []
# for year in final_dict:
#     for county in final_dict[year]:

#         positions.append(final_dict[year][county]["majority"])

# positions_unique= set(positions)
# # Example list
# data_list = positions

# relative_frequencies = calculate_relative_frequency(data_list)


map_counties = []
for feature in js['features']:
    map_counties.append(feature["properties"]["press_county"])
    




for county in map_counties:
    if county not in counties:
        print(county)
        
        
map_matches = {}

for year in final_dict.keys():
    map_matches[year] = []
    for county in final_dict[year].keys():
        if county not in map_counties:
            map_matches[year].append(county)
        
        





# End the timer
end_time = time.time()

# Calculate the execution time
execution_time = end_time - start_time



# Print the execution time
print(f"Execution time: {execution_time} seconds")
frequency_dict = frequency.set_index("county_year")["results"].to_dict()
# Save the dictionary as a JSON file
with open("new_data.json", "w") as json_file:
    json.dump(final_dict, json_file, indent = 2)

