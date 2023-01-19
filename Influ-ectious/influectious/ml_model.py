import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor


class Model():
    def __init__(self, train_data: pd.DataFrame):
        self.train_data = train_data
        self.rf_model: DecisionTreeRegressor = None
        self.target_var: str = "WEEKLY RATE"

    def train_model(self):
        data = pd.get_dummies(self.train_data)
        x = data.drop([self.target_var], axis=1)
        y = data[self.target_var]
        rf = RandomForestRegressor()
        rf.fit(x, y)
        self.rf_model = rf

    def predict(self):
        return self.rf_model.predict(self.test_data.drop([self.target_var], axis=1))

