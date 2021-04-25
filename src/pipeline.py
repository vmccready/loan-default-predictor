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
    
    data = data.reset_index(drop=True)

    #Create year columns
    data['year'] = data['issue_d'].apply(get_year)

    return data

def filter_data(data):
    # Filter to data we want to use
    # data = data[data['loan_status'].str.lower().isin(['fully paid', 'charged off'])]
    data = data[data['application_type'].str.lower()=='individual']
    return data

def completed_filter(data):
    data = data[data['loan_status'].str.lower().isin(['fully paid', 'charged off'])]
    return data

def clean_data(data):
    # Cleaning

    # Changel percent columns to floats
    percent = ['revol_util', 'int_rate']
    for p in percent:
        data[p] = data[p].apply(convert_pct)
    
    # Change terms column to int
    terms = {' 60 months': 60, ' 36 months': 36}
    data['term'] = data['term'].apply(lambda x: terms[x])

    return data

def get_year(s):
    m = re.search('\d+', s)
    return int(m[0])

def convert_pct(x):
    """
    Converts string with % to a float, handles 'None's.
    """
    if x is None or pd.isnull(x):
        return None
    return float(re.sub('%', '', x))


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



def create_X(data, drop):
    X = data.drop(drop, axis=1)

    # Fill missing values with 0
    X.fillna(value=0.0, inplace=True)

    # Create Categorical dummy columns
    categorical = ['home_ownership','sub_grade', 'purpose', 'verification_status']
    X = pd.get_dummies(X, columns=categorical, drop_first=True)  

    return X

def create_y(data):
    y = data['loan_status']
    y = y.apply(lambda x: 1 if x=='Charged Off' else 0)
    return y



