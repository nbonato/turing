import pandas as pd
import os
import pickle
from press_directories_cleaner import cleaned_press_directories

pickle_file = 'data/elections.pkl'

if os.path.exists(pickle_file):
    # Load pickle file if it exists
    with open(pickle_file, 'rb') as f:
        elections = pickle.load(f)
else:
    # this loads the full dataset with 640k rows
    elections = pd.read_excel("data/CLEA.xlsx")
    # this restricts the dataset to the UK electoral data
    elections = elections[elections['ctr_n'] == 'UK']
    # Save the elections dataset as a pickle file for future use
    with open(pickle_file, 'wb') as f:
        pickle.dump(elections, f)
        f.close()



elections = elections[elections['yr'] < 1923]
elections = elections[elections['yr'] > 1845]



#grouped_data = elections.groupby('yr')['mag'].apply(lambda x: x.unique().tolist())
#unique_values = elections['cst_n'].unique()


years_list = elections["yr"].unique()



elections_reduced = elections[["yr", "cst_n", "cst", "mag", "pty_n", "pty", "can","vot1", "pev1", "pv1", "pvs1"]]
# The dataset contains pv1 which is party votes, but also pvs which is the share
# I should use the share afterwards to check that the calculations are right

# It's actually more complicated because pev says how many voters,
# but each voter can actually vote more than one person and they often do, or
# maybe something similar, should probably ask blaxill


# this dictionary provides all the groupings based on year


# this dataset uses the districts from press directories to try and match costi
# tuencies. The idea is that using districts would be too granular and unrealistic,
# since newspapers are realistically present outside the main city as well


elections_replaced = elections_reduced.copy()

districts_counties = cleaned_press_directories[["county", "district", "year"]]



# I should make sure I am not accidentally erasing places with the same name 
# in two different counties



# Create an empty dictionary
district_county_dict = {}

# Iterate over the rows of the districts_counties dataset
for index, row in districts_counties.iterrows():
    year = row['year']
    district = row['district']
    county = row['county']
    
    # Check if the year is already a key in the dictionary
    if year in district_county_dict:
        # Append the district-county mapping to the existing dictionary
        district_county_dict[year][district] = county
    else:
        # Create a new entry in the dictionary for the year and district-county mapping
        district_county_dict[year] = {district: county}


# This dictionary matches each year with the replacements to do for that specific
# year
electoral_district_county = {}


for outer_key, outer_value  in district_county_dict.items():
    new_year = next((y for y in years_list if y >= outer_key), None)
    if new_year in electoral_district_county:
        merged_dict = electoral_district_county[new_year].copy()  # Make a copy of dict1
        for key, value in outer_value.items():
            if key in merged_dict:
                # Merge overlapping values in a list, converting it to set to 
                # keep unique values
                try:
                    values = set([merged_dict[key], value])
                    
                except:
                    print(merged_dict[key], new_year, outer_key, key)
                    values = [merged_dict[key], value]
                if len(values) == 1:
                    # if there's just one value, use that
                    values = str(values.pop())
                merged_dict[key] = values
                
            else:
                # Add the key-value pair from outer_value to merged_dict
                merged_dict[key] = value
        electoral_district_county[new_year] = merged_dict
    else:
        electoral_district_county[new_year] = outer_value


constituency_grouper = {
    "1847" : {

        "carnarvonshire": ["caernarvonshire", "caernarvon district of boroughs"],
        "cheshire": ["cheshire, northern", "cheshire, southern"],
        "cornwall": ["cornwall, eastern", "cornwall, western"],
        "cumberland": ["cumberland, eastern", "cumberland, western"],
        "derbyshire": ["derbyshire, northern", "derbyshire, southern"],
        "devonshire": ["devon, northern", "devon, southern"],
        "elgin": ["elgin district of burghs", "elginshire and nairnshire"],
        "essex": ["essex, northern", "essex, southern"],
        "gloucestershire": ["gloucestershire, eastern", "gloucestershire, western"],
        "gloucester": ["gloucester"],
        "guernsey": [],
        "hempshire": ["hempshire, northern", "hempshire, southern"],
        "jersey": [],
        "kent": ["kent, eastern", "kent, western"],
        "lincolnshire": ["lincolnshire, parts of kesteven a", "lincolnshire, parts of lindsey"],
        "nainshire": ["nairnshire"],
        "isle of man": []
    }
    
    
}

        
# Replace values in the 'cst_n' column based on the year-specific sub-dictionaries
for index, row in elections_replaced.iterrows():
    yr = row['yr']
    if yr in constituency_grouper:
        district_county_dict = constituency_grouper[yr]
        cst_n = row['cst_n']
        if cst_n in district_county_dict:
            county = district_county_dict[cst_n]
            elections_replaced.at[index, 'cst_n'] = county
        
