# This scripts cleans the press directories dataset and returns an object
# containing all possible variations

import pandas as pd
import pickle
import os
import re

pickle_file = 'data/press_directories.pkl'

if os.path.exists(pickle_file):
    # Load pickle file if it exists
    with open(pickle_file, 'rb') as f:
        press_directories = pickle.load(f)
else:
    # this loads the full dataset with 32 columns
    press_directories_general = pd.read_csv("data/pressDirectories.csv")
    # this restricts the dataset to the main columns used in the projects, keeping
    # the id one for compatibility with the original dataset
    press_directories = press_directories_general[["id", 
                                                   "S-TITLE", 
                                                   "county", 
                                                   "district", 
                                                   "wiki_id", 
                                                   "year", 
                                                   "S-POL" 
                                                   ]]
    # Save the press_directories as a pickle file for future use
    with open(pickle_file, 'wb') as f:
        pickle.dump(press_directories, f)
        f.close()
        

df = press_directories.copy()
# Define the regular expression pattern
pattern = r'in the province of ([\w\s\']+?) and county ([\w\s\']+)'

# Function to replace the matched phrases
def replace_phrase(match):
    county_name = match.group(2)
    if county_name[:3] == "of ":
        county_name = county_name[3:]
    if 'county' in county_name:
        return county_name
    else:
        return county_name + ' county'

# Apply the replacement on the column 'c'
df["county"] = df["county"].str.replace(pattern, replace_phrase, regex=True)




# Convert ndarray to a list
# key_list = counties_escaping_filtering.tolist()

escaped_replacements =  {
    "in the province of leinster and queen 's county" : "queen's county", 
    "in the province of leinster and king 's county" : "king's county", 
    "in the province of leinster and king's county" : "king's county", 
    'in the province of connaught and the county of sligo' : "sligo county", 
    'in the province of ulster and the county of armagh' : "armagh county", 
    'in the province of ulster and co . antrim' : "antrim county", 
    'in the province of ulster and the county armagh' : "armagh county",
    'in county down , province of ulster' : "down county"
    }

# Replace values using the dictionary
df["county"] = df["county"].replace(escaped_replacements)

selected_rows = df[df['county'].str.contains('in the province')]
counties_escaping_filtering = selected_rows["county"].unique()
cleaned_press_directories = df.copy()