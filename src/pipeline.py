import numpy as np 
import pandas as pd 
import pickle
from glob import iglob


def get_all_data(in_path):
    
    dfs = []

    # Read all files into dataframes
    for f in iglob(in_path + '*.csv'):
        temp_df = pd.read_csv(f, skiprows=[0], low_memory=False)
        dfs.append(temp_df)
    
    # Get the columns that are consistent in all years
    cols = list(dfs[0].columns)
    for i in range(1,len(dfs)):
        column_difference = set(cols).difference(set(dfs[i].columns))
        for c in column_difference:
            cols.remove(c)

    # Combine all dataframes, selecting only columns in all. 
    data = dfs[0][cols]
    for i in range(1, len(dfs)):
        data = data.append(dfs[i][cols])
    return data

def get_columns(in_all=True):
    with open('data/columns_in_all.pickle', 'rb') as handle:
        cols = pickle.load(handle)
    return cols

def drop_columns_with_missing(data, threshold=0.2):
    to_drop = []
    for c in data.columns:
        if data[c].isnull().sum()/data.shape[0] > threshold:
            to_drop.append(c)
    return data.drop(to_drop, axis=1)

def clean_data(data):


    cleaned = data.copy()
    return cleaned

