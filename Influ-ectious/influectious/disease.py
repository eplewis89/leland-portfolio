import os
from typing import Dict
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import requests


class DataSet:
    def __init__(self):
        self.raw_data: pd.DataFrame = None
        self.clean_data: pd.DataFrame = None
        self.source_location: str = None
        self.save_location: str = None
        self.api_endpoint: str = None
        self.api_header: dict = None


class Disease:
    def __init__(self, disease_name: str):
        self.disease_name: str = disease_name
        self.data: Dict[DataSet] = {}
        self.reconciled_data: pd.DataFrame = None

        if self.disease_name is "Influenza":
            self.data["cdc_hospitalization_rates"] = DataSet()
            self.data["cdc_hospitalization_rates"] \
                .source_location = \
                "Data" \
                "/CDC_FluView" \
                "/Hospitalizations" \
                "/Hospitalization_Rates" \
                "/Compiled_Data_For_DB.csv"
            self.data["cdc_hospitalization_rates"].api_endpoint = \
                "https://data.cdc.gov"

    def ingest_data(self, ingest_source):
        if ingest_source == "csv":
            self.ingest_csv()
        elif ingest_source == "api":
            self.ingest_api()

    def ingest_csv(self):
        if not self.data:
            return
        for analysis_name in self.data:
            relative_path = \
                self.data[analysis_name].source_location
            data_path = os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__),
                    "..",
                    relative_path
                )
            )
            self.data[analysis_name].raw_data \
                = pd.read_csv(data_path)
            self.data[analysis_name].save_location \
                = str(data_path).replace('.csv', "_CLEANED.csv")

    def ingest_api(self):
        for analysis_name in self.data:
            if analysis_name is "cdc_hospitalization_rates":
                url = self.data["cdc_hospitalization_rates"].api_endpoint
                params = {
                    "dataSet": "NCHS-HOSP",
                    "location": "US",
                    "yearStart": "2010",
                    "yearEnd": "2019",
                    "topic": "Hospitalizations",
                    "format": "JSON",
                    "apiKey": "YOUR_API_KEY"
                }

                response = requests.get(url, params=params)

                if response and response.satus == 200:
                    pd.read_json(response.json())

    def clean_up_data(self):
        for analysis_name in self.data:
            if analysis_name is "cdc_hospitalization_rates":
                clean_df = self.data[analysis_name].clean_data
                raw_df = self.data[analysis_name].raw_data
                clean_df = \
                    raw_df.drop(['YEAR'], axis=1)
                clean_df = \
                    clean_df.dropna()  # drops null as well
                clean_df.columns = \
                    clean_df.columns.str.strip()

                # Non-numerical columns are made categorical
                clean_df['CATCHMENT'] = \
                    clean_df['CATCHMENT'].astype('category')
                clean_df['SEX CATEGORY'] = \
                    clean_df['SEX CATEGORY'].astype('category')
                clean_df['SEX CATEGORY'] = \
                    clean_df['SEX CATEGORY'].astype('category')
                clean_df['RACE CATEGORY'] = \
                    clean_df['RACE CATEGORY'].astype('category')

                # Create new time-series column with 'yyyy-ww' format
                clean_df['date'] = \
                    clean_df['MMWR-YEAR'].astype(str) + \
                    '-' + clean_df['MMWR-WEEK'].astype(str) + \
                    '-1'
                clean_df.set_index('date', inplace=True)
                clean_df.index = pd.to_datetime(clean_df.index, format='%Y-%U-%w')
                clean_df.sort_index()
                self.data[analysis_name].clean_data = clean_df

    def store_data(self):
        for data_source in self.data:
            self.data[data_source].clean_data. \
                to_csv(self.data[data_source].save_location, sep='\t')

    def reconcile(self):
        # when more than one set of data is analyzed it will
        # need to be reconciled into a single data set for analysis
        for data_set in self.data:
            if self.reconciled_data is None:
                self.reconciled_data = self.data[data_set].clean_data
            else:
                pd.concat(
                    [self.reconciled_data, self.data[data_set].clean_data],
                    ignore_index=True, sort=False
                )

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
