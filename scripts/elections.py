import pandas as pd
import os
import pickle
import sys
import winsound 

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
from press_directories_cleaner import cleaned_press_directories, irish_counties


pickle_file = os.path.join(current_dir, 'data', 'elections.pkl')

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

elections = elections.reset_index(drop = True)




#grouped_data = elections.groupby('yr')['mag'].apply(lambda x: x.unique().tolist())
#unique_values = elections['cst_n'].unique()


years_list = elections["yr"].unique()


elections_reduced = elections[["id","yr", "cst_n", "sub", "cst", "mag", "pty_n", "pty", "can","vot1", "pev1", "pv1", "pvs1", "can", "cvs1" ]]
# The dataset contains pv1 which is party votes, but also pvs which is the share
# I should use the share afterwards to check that the calculations are right

# It's actually more complicated because pev says how many voters,
# but each voter can actually vote more than one person and they often do, or
# maybe something similar, should probably ask blaxill


# this dictionary provides all the groupings based on year


# this dataset uses the districts from press directories to try and match costi
# tuencies. The idea is that using districts would be too granular and unrealistic,
# since newspapers are realistically present outside the main city as well


elections_replaced = elections_reduced.copy().reset_index(drop = True)


districts_counties = cleaned_press_directories[["county", "district", "year"]]



# I should make sure I am not accidentally erasing places with the same name 
# in two different counties
# This is how I am doing it

df = districts_counties.copy()

# This groups the counties by district
district_counties_duplicate = df.groupby('district')['county'].agg(["unique"])
# This adds a column counting how many counties are there for each district
district_counties_duplicate['county_count'] = district_counties_duplicate['unique'].apply(len)


# Filter districts with county_count higher than 1
filtered_districts = district_counties_duplicate[district_counties_duplicate['county_count'] > 1].reset_index()

# Convert bot to sets
districts = set(filtered_districts["district"].to_list())
electoral_check = set(elections_reduced["cst_n"].to_list())
        
# These are the districts that appear in the election dataset
matching_elements = districts.intersection(electoral_check)



# Create an empty dictionary
district_county_dict = {}







# Remove all districts that are not present in the elections dataset
# It would be useless to keep them since they won't help in getting
# from the constituency name to the relevant county

districts = set(districts_counties["district"].to_list())
keep = districts.intersection(electoral_check)
differe = districts.difference(electoral_check)


# Iterate over the rows of the districts_counties dataset
for index, row in districts_counties.iterrows():
    year = row['year']
    district = row['district']
    county = row['county']
    
    # for now, I am skipping districts that are duplicate
    if district in matching_elements:
        continue
    
    # skip districts that are not in the elections dataset
    if district not in keep:
        continue
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



 #   _____ _               _                     _                                     _       
 #  / ____| |             | |                   | |                                   | |      
 # | |    | |__   ___  ___| | __  _ __ ___ _ __ | | __ _  ___ ___ _ __ ___   ___ _ __ | |_ ___ 
 # | |    | '_ \ / _ \/ __| |/ / | '__/ _ \ '_ \| |/ _` |/ __/ _ \ '_ ` _ \ / _ \ '_ \| __/ __|
 # | |____| | | |  __/ (__|   <  | | |  __/ |_) | | (_| | (_|  __/ | | | | |  __/ | | | |_\__ \
 #  \_____|_| |_|\___|\___|_|\_\ |_|  \___| .__/|_|\__,_|\___\___|_| |_| |_|\___|_| |_|\__|___/
 #                                        | |                                                  
 #                                        |_|                                                  





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



replace_typos = {
    "rowburghshire" : "roxburghshire",
    "bershire, wokingham" : "berkshire, wokingham",
    "durgavan" : "dungarvan",
    "londonberry" : "londonderry",
    "londonberry city" : "londonderry",
    "londonberry county" : "londonderry",
    "londonberry north" : "londonderry",
    "londonberry south" : "londonderry"
    }




elections_replaced["press_county"] = elections_replaced["cst_n"].replace(replace_typos)   




# Remove Irish counties from the dataset
#counties_before_irish = elections_replaced["press_county"].unique()

# Removing these two counties temporarily is necessary to avoid matching UK counties 
# such as king's lynn and queen's university of belfast
elements_to_remove = ["king's", "queen's"]

# List of regex patterns to match in 'press_county', excluding elements_to_remove
counties_regex = [rf"\b{county}.*" for county in irish_counties if county not in elements_to_remove]

# add the regex for king's and queen's county
counties_regex += [r"\bking's county.*", r"\bqueen's county.*"]

# Create the regex pattern by joining the list elements with '|'
regex_pattern = '|'.join(counties_regex)

# exclude matched counties using the regex
elections_replaced = elections_replaced[~elections_replaced['press_county'].str.contains(regex_pattern, case=False, regex=True)]

# # check if the match worked correctly
# matched_regex_counties = elections_replaced[elections_replaced['press_county'].str.contains(regex_pattern, case=False, regex=True)]

# matched_regex_counties = list(matched_regex_counties["press_county"].unique())


# add back the two excluded counties
irish_counties += elements_to_remove

# add county to the end of each county's name
irish_counties_county = [county + " county" for county in irish_counties]

# remove the irish counties
elections_replaced = elections_replaced[~elections_replaced['press_county'].isin(irish_counties_county)]




# These two steps remove the university constituencies, which are not trackable to
# a specific area. There are two steps to try and catch all cases
elections_replaced = elections_replaced[~elections_replaced["press_county"].str.contains("universit")]
elections_replaced = elections_replaced[~elections_replaced["sub"].str.contains("universit")]





# constituency_grouper = {
#     "denbighshire" : ["denbigh district of boroughs", "denbigshire"],
#     "carnarvonshire": ["caernarvonshire", "caernarvon district of boroughs"],
#     "cheshire": ["cheshire, northern", "cheshire, southern"],
#     "cornwall": ["cornwall, eastern", "cornwall, western"],
#     "cumberland": ["cumberland, eastern", "cumberland, western"],
#     "derbyshire": ["derbyshire, northern", "derbyshire, southern"],
#     "devonshire": ["devon, northern", "devon, southern"],
#     # Elginshire and nairnshire have a difficult situation where 
#     # the election datasets contains data for distric of burghs and
#     # elginshire and nairnshire, while press contains separate records
#     # for elgin and nairn county. The only possibility might be to join them
#     # "elgin": ["elgin district of burghs", "elginshire and nairnshire"],
#     "essex": ["essex, northern", "essex, southern"],
#     "gloucestershire": ["gloucestershire, eastern", "gloucestershire, western"],
#     "gloucester": ["gloucester"],
#     "hempshire": ["hempshire, northern", "hempshire, southern"],
#     "kent": ["kent, eastern", "kent, western"],
#     "lincolnshire": ["lincolnshire, parts of kesteven a", "lincolnshire, parts of lindsey"],
#     #"inverness-shire" : ["iverness-shire","iverness district of burghs"]
    
# }






# # Assign values in the press_county based on the replacemnt in the 'cst_n' column
# # using the dictionary
# for index, row in elections_replaced.iterrows():
#     cst_n = row['cst_n']
#     for key, values in constituency_grouper.items():
#         if cst_n in values:
#             elections_replaced.at[index, 'press_county'] = key
#             #print(f"replacing {cst_n} with {key} at index {index}")



# This might ultimately be unnecessary


# constituency_grouper_year = {
#     "1847" : {

#         "carnarvonshire": ["caernarvonshire", "caernarvon district of boroughs"],
#         "cheshire": ["cheshire, northern", "cheshire, southern"],
#         "cornwall": ["cornwall, eastern", "cornwall, western"],
#         "cumberland": ["cumberland, eastern", "cumberland, western"],
#         "derbyshire": ["derbyshire, northern", "derbyshire, southern"],
#         "devonshire": ["devon, northern", "devon, southern"],
#         # Elginshire and nairnshire have a difficult situation where 
#         # the election datasets contains data for distric of burghs and
#         # elginshire and nairnshire, while press contains separate records
#         # for elgin and nairn county. The only possibility might be to join them
#         # "elgin": ["elgin district of burghs", "elginshire and nairnshire"],
#         "essex": ["essex, northern", "essex, southern"],
#         "gloucestershire": ["gloucestershire, eastern", "gloucestershire, western"],
#         "gloucester": ["gloucester"],
#         "hempshire": ["hempshire, northern", "hempshire, southern"],
#         "kent": ["kent, eastern", "kent, western"],
#         "lincolnshire": ["lincolnshire, parts of kesteven a", "lincolnshire, parts of lindsey"],
#         #"inverness-shire" : ["iverness-shire","iverness district of burghs"]
        
#     }
    
    
# }


     



# # Replace values in the 'cst_n' column using the generic dictionary
# for index, row in elections_replaced.iterrows():
#     yr = str(row['yr'])
#     if yr in constituency_grouper_year.keys():

#         replace = constituency_grouper_year[yr]
#         cst_n = row['cst_n']
#         for key, values in replace.items():
#             if cst_n in values:
#                 elections_replaced.at[index, 'cst_n'] = key
#                 #print(f"replacing {cst_n} with {key} at index {index}")
###############################################################################
  
compare = elections_replaced.copy()





# This uses the dictionary electoral_district_county to match each district to 
# a county using a sub-dictionary tailored to the year

for index, row in elections_replaced.iterrows():
    yr = row['yr']
    if yr in electoral_district_county.keys():
        cst_n = row['cst_n']
        replace = electoral_district_county[yr]
        if cst_n in replace.keys():        
            # print(f"replacing {cst_n}", end="")
            # print(f" with {replace[cst_n]}")
            elections_replaced.at[index, 'press_county'] = replace[cst_n]



# pickle_file = os.path.join(current_dir, 'data', 'elections_replaced.pkl')
          
# with open(pickle_file, 'rb') as f:
#     elections_replaced = pickle.load(f)

# with open(pickle_file, 'wb') as f:
#     pickle.dump(elections_replaced, f)
#     f.close()

            
# test = elections_replaced[elections_replaced["cst_n"] == "ross and cromarty"]



# elections_test = elections_replaced
# #[elections_replaced['yr'] > 1910]  
# elections_test.to_csv("rosshire.csv")



# These are changes that need to be scrutinised

dubious_changes = {
    
    # The constituency was actually called ross and cromarty
    "ross and cromarty" : "ross-shire",
    
    # Inverness-shire seems to have been split and recomposed with Inverness 
    # and Ross and Cromarty. I am not completely sure that they are fully equivalent
    "iverness-shire and ross and croma" : "ross-shire",
    
    "anglesey" : "isle of anglesey",
    "bute" : "isle of bute",
    "argyll" : "argyllshire",
    }        





elections_replaced["press_county"] = elections_replaced["press_county"].replace(dubious_changes)   





#sys.exit()





locations = elections_replaced[["press_county", "sub"]]





# Ding sound when the script is finished
frequency = 600  # Set the frequency of the sound (in Hz)
duration = 100  # Set the duration of the sound (in milliseconds)
winsound.Beep(frequency, duration)





elections_cleaned = elections_replaced.copy()


with open("elections_cleaned.pkl", 'wb') as f:
    pickle.dump(elections_cleaned, f)
    f.close()


# test = elections[elections["cst_n"].str.contains("elgin")]



