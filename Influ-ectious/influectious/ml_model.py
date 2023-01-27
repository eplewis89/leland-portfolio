import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import seaborn as sns
import xgboost as xgb


class Model:
    def __init__(self):
        self.training_data = None
        self.testing_data = None
        self.model = None
        self.model_fit = None
        self.target_var: str = "CUMULATIVE RATE"

    def train_model(self, training_data: pd.DataFrame):
        self.training_data = training_data

    def test_model(self, test_data: pd.DataFrame):
        self.testing_data = test_data

    def predict(self, steps):
        prediction = self.model_fit.forecast(steps=steps)
        return prediction[0]


class ArimaModel(Model):
    def __init__(self):
        super().__init__()
        self.model = 'ARIMA'

    def train_model(self, training_data: pd.DataFrame):
        super().train_model(training_data)
        self.model = ARIMA(training_data[self.target_var], order=(1, 1, 1))
        self.model_fit = self.model.fit()

    def test_model(self, testing_data: pd.DataFrame):
        super().train_model(testing_data)
        pass
