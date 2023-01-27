from typing import List

import pandas
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import seaborn as sns
import xgboost as xgb


class Model:
    def __init__(self, independent_var: str, dependant_var: str):
        self.input_data = None
        self.split_columns = None
        self.training_data = None
        self.testing_data = None
        self.models = None
        self.models_fit = None
        self.independent_var = independent_var
        self.dependant_var = dependant_var

    def subset_and_store(self, input_data: pandas.DataFrame, split_column_names: List[str]):

    def train_model(self):


    def test_model(self, test_data: pd.DataFrame):
        self.testing_data = test_data

    def predict(self, steps):
        prediction = self.models_fit.forecast(steps=steps)
        return prediction[0]


class ArimaModel(Model):
    def __init__(self, independent_var: str, dependant_var: str):
        super().__init__(dependant_var, independent_var)
        self.model = 'ARIMA'

    def train_model(self, training_data: pd.DataFrame):
        super().train_model(training_data)
        self.model = ARIMA(training_data[self.dependant_var], order=(1, 1, 1))
        self.model_fit = self.model.fit()

    def test_model(self, testing_data: pd.DataFrame):
        super().train_model(testing_data)
        pass
