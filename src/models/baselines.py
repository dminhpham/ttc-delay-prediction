import pandas as pd
import numpy as np


class GlobalMedian:
    """Predict the training median delay for every incident."""
    def fit(self, X, y):
        self.median_ = y.median()
        return self

    def predict(self, X):
        return np.full(len(X), self.median_)


class GlobalMean:
    """Predict the training mean delay for every incident."""
    def fit(self,X, y):
        self.mean_ = y.mean()
        return self

    def predict(self, X):
        return np.full(len(X), self.mean_)


class RouteHourMedian:
    """Predict the training median delay for each (route, hour) pair; unseen pairs get the global median."""
    def fit(self, X, y):
        key = X["route"].astype(str) + "_" + X["hour"].astype(str)
        self.table_ = y.groupby(key).median().to_dict()
        self.median_ = y.median()
        return self

    def predict(self, X):
        key = X["route"].astype(str) + "_" + X["hour"].astype(str)
        return key.map(self.table_).fillna(self.median_).to_numpy()