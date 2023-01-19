import pandas as pd
from pathlib import Path

x = 3
def data_ingestion():
    path = Path(__file__).parent / "../Data/CDC_FluView/Hospitalizations/Compiled_Data_For_DB.csv"
    # Download and read the data into a dataframe
    data = pd.read_csv(path)
    print("Hello World")
