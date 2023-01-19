import os
from typing import Dict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


def run(disease_model: str):
    disease = Disease(disease_model)
    disease.ingest_data()
    disease.analyze_data()


class Disease:
    def __init__(self, disease_name: str):
        self.disease_name: str = disease_name
        self.data: Dict[Disease.DataSet] = {}

        if self.disease_name is "Influenza":
            self.data["cdc_hospitalization_rates"] = self.DataSet()

    class DataSet:
        def __init__(self):
            self.raw_data: Dict[str, pd.DataFrame] = None
            self.clean_data: Dict[str, pd.DataFrame] = None
            self.source_location: str = None
            self.save_location: str = None

    def ingest_data(self):
        if not self.data:
            return
        for analysis_name in self.data:
            if analysis_name is "cdc_hospitalization_rates":
                relative_path = "Data/CDC_FluView/Hospitalizations/" \
                                "Hospitalization_Rates/Compiled_Data_For_DB.csv"

                data_path = os.path.abspath(
                    os.path.join(os.path.dirname(__file__), "..", relative_path)
                )

                self.data[analysis_name].raw_data = pd.read_csv(data_path)
                self.data[analysis_name].save_location = str(data_path).replace('.csv', "_CLEANED.csv")

        self.clean_up_data()

        for data_source in self.data:
            self.store_data(data_source)

    def clean_up_data(self):
        for analysis_name in self.data:
            if analysis_name is "cdc_hospitalization_rates":
                self.data[analysis_name].clean_data = \
                    self.data[analysis_name].raw_data.drop(['YEAR'], axis=1)
                self.data[analysis_name].clean_data = \
                    self.data[analysis_name].raw_data.dropna()  # drops null as well
                self.data[analysis_name].clean_data.columns = \
                    self.data[analysis_name].raw_data.columns.str.strip()

    def store_data(self, data_source: DataSet):
        self.data[data_source].clean_data.\
            to_csv(self.data[data_source].save_location, sep='\t')

    def analyze_data(self):
        for data_set in self.data:
            clean_data = self.data[data_set].clean_data
            # Use seaborn to create a boxplot of the weekly rate by catchment
            sns.boxplot(x='CATCHMENT', y='WEEKLY RATE', data=clean_data)
            plt.xlabel('Catchment')
            plt.ylabel('Weekly Rate')
            plt.title('Weekly Rate by Catchment')
            plt.show()

            # Use seaborn to create a barplot of the cumulative rate by sex category
            sns.barplot(x='SEX CATEGORY', y='CUMULATIVE RATE', data=clean_data)
            plt.xlabel('Sex Category')
            plt.ylabel('Cumulative Rate')
            plt.title('Cumulative Rate by Sex Category')
            plt.show()

            # Calculate summary statistics
            print(clean_data.describe())
            # Group data by season and calculate rudimentary statistics
            print("\n____MEAN____")
            print(clean_data.groupby(['AGE CATEGORY'])
                  .mean()['CUMULATIVE RATE'])
            print("\n____MEDIAN____")
            print(clean_data.groupby(['AGE CATEGORY'])['CUMULATIVE RATE']
                  .median())
            print("\n____MODE____")
            print(clean_data.groupby(['AGE CATEGORY'])['CUMULATIVE RATE']
                  .apply(lambda x: x.mode()))

            # Create pivot table of weekly rate by age category and race category
            pivot_table = clean_data.pivot_table(
                values='WEEKLY RATE',
                index='AGE CATEGORY',
                columns='RACE CATEGORY')

            # Use pandas to display the pivot table
            pivot_table.plot(kind='bar', stacked=True)
            plt.xlabel('Age Category')
            plt.ylabel('Weekly Rate')
            plt.title('Weekly Rate by Age Category and Race Category')
            plt.show()

