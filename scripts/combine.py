# This file combines the press directories dataset with the dataset
# containing electoral data


# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
import winsound

from elections import elections_replaced
from press_directories_cleaner import press_directories, cleaned_press_directories


#value_counts = press_directories['S-POL'].value_counts()


df = press_directories

# Group by 'year' and 'county' and count the occurrences of 'S-TIME'
#result_df = press_directories.groupby(['year', 'county'])['S-POL'].count().reset_index()

# Rename the count column to 'Count'
#result_df = result_df.rename(columns={'Political leaning': 'Count'})



#london = df[(df['year'] == 1888) & (df['county'] == 'london')][['S-TITLE', 'S-POL']]

#frequency = london['S-POL'].value_counts()



'''
counties = df["county"].unique()
districts = df["district"].unique()
years = df["year"].unique()
election_years = elections["yr"].unique()


common_constituencies = np.intersect1d(districts, unique_values)



not_in_districts = np.setdiff1d(unique_values, districts)
not_in_unique_values = np.setdiff1d(districts, unique_values)










1847
1852
1857
1859
1865
1868
1874
1880
1885
1886
1892
1895
1900
1906
1910
1918
1922




'''





# # testing out two specific dates
# first_press = df[df['year'] >= 1846]
# first_election = elections[elections['yr'] >= 1847]

# first_press_counties = first_press["county"].unique()
# first_election_counties = first_election["cst_n"].unique()

# first_common_constituencies = np.intersect1d(first_press_counties, first_election_counties)


# only_in_press = np.setdiff1d(first_press_counties, first_election_counties)
# only_in_elections = np.setdiff1d(first_election_counties, first_press_counties)



# compare with cleaned 


df = cleaned_press_directories.copy()
# testing out two specific dates
cleaned_first_press = df
#[df['year'] <= 1922]
cleaned_first_election = elections_replaced
#elections_replaced['yr'] <= 1922]



cleaned_first_press_counties = cleaned_first_press["county"].unique()
cleaned_first_press_counties = np.sort(cleaned_first_press_counties)

cleaned_first_election_counties = cleaned_first_election["press_county"].unique()
cleaned_first_election_counties = np.sort(cleaned_first_election_counties)


cleaned_first_common_constituencies = np.intersect1d(cleaned_first_press_counties, cleaned_first_election_counties)


only_in_press_cleaned = np.setdiff1d(cleaned_first_press_counties, cleaned_first_election_counties)
only_in_elections_cleaned = np.setdiff1d(cleaned_first_election_counties, cleaned_first_press_counties)


# Sort both arrays alphabetically
sorted_elections = sorted(only_in_elections_cleaned)
sorted_press = sorted(only_in_press_cleaned)



# Ding sound when the script is finished
frequency = 1500  # Set the frequency of the sound (in Hz)
duration = 1000  # Set the duration of the sound (in milliseconds)
winsound.Beep(frequency, duration)

# deleting useless variables to avoid cluttering the variable explorer
#del  first_press, first_election,first_press_counties, first_election_counties, first_common_constituencies
