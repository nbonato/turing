# -*- coding: utf-8 -*-
"""
Created on Thu Aug 24 17:25:25 2023

@author: Nico
"""

import pickle

with open("pickles/elections.pkl") as f:
    elections = pickle.load(f)
    
with open("pickles/cleaned_press_directories.pkl") as f:
    press = pickle.load(f)    