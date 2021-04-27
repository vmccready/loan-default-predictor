import numpy as np 
import pandas as pd 
import pickle
import datetime
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

    #Create year and date columns
    data['year'] = data['issue_d'].apply(get_year)
    data['date'] = data['issue_d'].apply(get_date)

    return data

def individual_data(data):
    # Filter to data we want to use
    # data = data[data['loan_status'].str.lower().isin(['fully paid', 'charged off'])]
    data = data[data['application_type'].str.lower()=='individual']
    return data

def completed_filter(data):
    data = data[data['loan_status'].str.lower().isin(['fully paid', 'charged off'])]
    return data

def date_filter(start, stop, data):
    return data[
        (data['date'] >= start) &
        (data['date'] <  stop)]

def term_filter(term, data):
    return data[data['term']==term]

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

month_dict = {'Jan':1, 'Feb':2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 
              'Jul':7, 'Aug':8, 'Sep':9, 'Oct':10, 'Nov':11, 'Dec':12}
def get_date(date_str):
    y = int(re.search('\d+', date_str)[0])
    m = re.search('[a-zA-Z]+', date_str)[0]
    m = month_dict[m]
    return datetime.date(y,m,1)

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
    with open('data/X_drop.pickle', 'rb') as handle:
        cols = pickle.load(handle)
    return cols

def drop_columns_with_missing(data, threshold=0.2):
    to_drop = []
    for c in data.columns:
        if data[c].isnull().sum()/data.shape[0] > threshold:
            to_drop.append(c)
    return data.drop(to_drop, axis=1)

def create_dummies(data):
    categorical = ['home_ownership','sub_grade', 'purpose', 'verification_status']
    data = pd.get_dummies(data, columns=categorical, drop_first=True) 
    return data

def create_X(data, drop):
    X = data.drop(drop, axis=1)

    # Fill missing values with 0
    X.fillna(value=0.0, inplace=True)

    # # Create Categorical dummy columns
    # categorical = ['home_ownership','sub_grade', 'purpose', 'verification_status']
    # X = pd.get_dummies(X, columns=categorical, drop_first=True)  

    return X

def create_y(data):
    y = data['loan_status']
    y = y.apply(lambda x: 1 if x=='Charged Off' else 0)
    return y

def print_missing(data):
    for column in data.columns:
        if data[column].isna().sum() != 0:
            missing = data[column].isna().sum()
            portion = (missing / data.shape[0]) * 100
            print(f"'{column}': number of missing values '{missing}' ==> '{portion:.3f}%'")

