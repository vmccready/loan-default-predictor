import numpy as np 
import pandas as pd 
import pickle
import re
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
    
    data.reset_index(drop=True)

    return data

def clean_data(data):
    # Cleaning
    percent = ['revol_util', 'int_rate']
    for p in percent:
        data[p] = data[p].apply(convert_pct)

    # Filter to data we want to use
    data = data[data['loan_status'].apply(lambda x: x in ['Fully Paid', 'Charged Off'])]
    data = data[data['application_type'].apply(lambda x: x.lower()=='individual')]

    # Remove columns that contain too much missing data
    data = drop_columns_with_missing(data, 0.2)
    data = data.dropna()
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

def convert_pct(x):
    """
    Converts string with % to a float, handles 'None's.
    """
    if x is None or pd.isnull(x):
        return None
    return float(re.sub('%', '', x))

def create_Xy(data, X_columns):
    # useable_data = data[data['loan_status'].apply(lambda x: x in ['Fully Paid', 'Charged Off'])]
    # X = useable_data[X_columns][useable_data['application_type']=='INDIVIDUAL']
    # X = drop_columns_with_missing(X, 0.2)
    X = data[X_columns].copy()
    # Create dummy columns for categorical data
    categorical = ['home_ownership','sub_grade', 'term', 'purpose']
    X = pd.get_dummies(X, columns=categorical, drop_first=True)  
    # X = X.drop(['term' ], axis=1)

    # For now, drop all rows with missing data
    X = X.dropna()

    y = data['loan_status']
    y = y.apply(lambda x: 1 if x=='Charged Off' else 0)
    return X, y

def create_y(data, X_index):
    y = data['loan_status'].iloc[X_index].copy()
    y = y.apply(lambda x: 1 if x=='Charged Off' else 0)
    return y



