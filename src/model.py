import numpy as np 
import pandas as pd 

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import recall_score, precision_score


def create_model(model, X, y):

    X_train, X_test, y_train, y_test = train_test_split(X,y)

    model.fit(X_train, y_train)
    accuracy = model.score(X_test, y_test)
    recall = recall_score(y_test, model.predict(X_test))
    precision = precision_score(y_test, model.predict(X_test))

    return model, accuracy, recall, precision

