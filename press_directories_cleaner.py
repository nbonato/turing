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


# These are replacements that are not as easily captured by simple regex, so 
# I preferred to spell them out to make it more transparent


escaped_replacements =  {
    "in the province of leinster and queen 's county" : "queen's county", 
    "in the province of leinster and king 's county" : "king's county", 
    "in the province of leinster and king's county" : "king's county", 
    'in the province of connaught and the county of sligo' : "sligo county", 
    'in the province of ulster and the county of armagh' : "armagh county", 
    'in the province of ulster and co . antrim' : "antrim county", 
    'in the province of ulster and the county armagh' : "armagh county",
    'in county down , province of ulster' : "down county",
    'in the county of tyrone and province of ulster' : 'tyrone county',
    'in the prov . of munster and co . clare' : 'clare county',
    'in the prov. of ulster and co. antrim' : 'antrim county',
    'county wicklow and province of leinster' : 'wicklow county',
    'prov . of connaught & county leitrim' : 'leitrim county'
    }


# Replace values using the dictionary
df["county"] = df["county"].replace(escaped_replacements)

# These replacements are based on searching the name of specific places and
# piecing together manually what they correspond to. They might be wrong
# and should be re-inspected

manual_replacements =  {
    "brecknockshire" : "breconshire",
    "caithness-shire" : "caithness",
    "dorsetshire": "dorset",
    "fifeshire" : "fife"

}



# Replace values using the dictionary
df["county"] = df["county"].replace(manual_replacements)


special_cases = '''

    "ross-shire" : "ross and cromarty", # There might be a cromartshire also
    "roxburghshire" : "rowburghshire", #Typo
    "londonderry county" : "londonberry county", #Typo, also there's the city
    "edinburghshire" : "edingburghshire", # This is most likely a typo on the CLEA side, there's also the city
    "inverness-shire" : "iverness-shire" # Typo, but also this can be district of burghs too
    
    
carnarvonshire can be both caernarvonshire and caernarvon district of boroughs
    at different times

cheshire was split into cheshire, northern and cheshire, southern in 1832. 
    
cornwall was split into cornwall, eastern and cornwall, western in 1832. 
    
cumberland was split into cumberland, eastern and cumberland, western in 1832. 
    
derbyshire was split into derbyshire, northern and derbyshire, southern in 1832. 
    
devonshire was split into devon, northern and devon, southern in 1832

elgin can be both elgin district of burghs and elginshire and nairnshire

essex was split into essex, northern and essex, southern in 1832.

gloucestershire was split into gloucestershire, eastern and gloucestershire, western
    gloucester was also a constituency on itself

guernsey has no representation in the UK parliament

hempshire was split into hempshire, northern and hempshire, southern in 1832. 

jersey has no representation in the UK parliament

kent was split into kent, eastern and kent, western

lincolnshire was split into "lincolnshire, parts of kesteven a" and "lincolnshire, parts of lindsey"

nainshire might be nairnshire, which was joined with elgin in elginshire and nairnshire

isle of man has no representation in the UK parliament
'''


special_cases = special_cases.split("\n\n")

# adding isle of man manually to avoid split via space
special_cases_list = ["isle of man"]
for line in special_cases:
    special_cases_list.append(line.split(" ")[0])
special_cases_list.pop() # remove "isle" added by split



selected_rows = df[df['county'].str.contains('in the province')]
counties_escaping_filtering = selected_rows["county"].unique()
cleaned_press_directories = df.copy()