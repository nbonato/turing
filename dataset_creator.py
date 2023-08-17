import pandas as pd
import time
import json 

from scripts.press_directories_cleaner import cleaned_press_directories
from map_creator import counties_map  



# Start the timer
start_time = time.time()


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
    threshold = 2  # 2% threshold
    
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
    return frequency_dict



frequency = (
    df.groupby(["year", "county"])
    .apply(calculate_frequency)
    .reset_index(name="results")
)



test_dict = frequency.groupby('year')[['county','results']].apply(lambda x: x.set_index('county')["results"].to_dict()).to_dict()



# Add a column for the combination of "county" and "year"
frequency["county_year"] = frequency["county"] + "_" + frequency["year"].astype(str)


# End the timer
end_time = time.time()

# Calculate the execution time
execution_time = end_time - start_time

# Print the execution time
print(f"Execution time: {execution_time} seconds")
frequency_dict = frequency.set_index("county_year")["results"].to_dict()
# Save the dictionary as a JSON file
with open("new_data.json", "w") as json_file:
    json.dump(test_dict, json_file, indent = 2)

