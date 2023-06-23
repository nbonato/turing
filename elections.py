import pandas as pd
import os
import pickle


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
unique_values = elections['cst_n'].unique()