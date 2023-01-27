import os
from typing import Dict
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cm as cm
import seaborn as sns
import requests


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
            self.data["cdc_hospitalization_rates"].api_source = 'CDC'
            self.data["cdc_hospitalization_rates"].api_endpoint = \
                "https://data.cdc.gov"
            self.data["cdc_hospitalization_rates"].api_parameter_name = 'request_xml'
            self.data["cdc_hospitalization_rates"].api_parameters = \
                '''<request-parameters>
                    <parameter>
                        <name>accept_datause_restrictions</name>
                        <value>true</value>
                    </parameter>
                    <parameter>
                        <name>stage</name> 
                        <value>about</value> 
                    </parameter> 
                    <parameter> 
                        <name>saved_id</name> 
                        <value></value> 
                    </parameter>
                </request-parameters> '''

    def ingest_data(self, ingest_source):
        if ingest_source == "csv":
            self.ingest_csv()
        elif ingest_source == "api":
            self.ingest_api()

    def ingest_csv(self):
        if not self.data:
            return
        for analysis_name in self.data:
            self.data[analysis_name].ingest_type = 'csv'
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
        # Work in Progress
        for analysis_name in self.data:
            self.data[analysis_name].ingest_type = 'api'
            source = self.data[analysis_name].api_source

            if source is "CDC":
                url = self.data["cdc_hospitalization_rates"].api_endpoint + '/D76'  ## or D140
                param_name = self.data["cdc_hospitalization_rates"].api_parameter_name
                xml_request = self.data["cdc_hospitalization_rates"].api_parameters
                head = {
                    'API_KEY': 'Enter yours here',
                    'API_SECRET': 'Enter yours here'
                }
                response = requests.get(url, headers=head,
                                        data={param_name: xml_request, "accept_datause_restrictions": "true"})

                if response and response.status == 200:
                    pd.read_json(response.json())
                else:
                    raise Exception(
                        f"Response not 200 - Response code: {response.status_code} - Reason: {response.reason}")

    def clean_up_data(self):
        for analysis_name in self.data:
            if analysis_name is "cdc_hospitalization_rates":
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
                clean_df['date'] = pd.to_datetime(clean_df['date'], format='%Y-%U-%w')
                clean_df['date'] = clean_df['date'].dt.date
                clean_df.sort_values(by='date')
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
            if data_set is "cdc_hospitalization_rates":
                clean_data = self.data[data_set].clean_data
                color_pallet = sns.color_palette()
                cdc_hosp_analysis = CdcAnalysisModule()
                self.data[data_set].location_scatter_plot = \
                    cdc_hosp_analysis.overall_scatter_plot(clean_data, color_pallet)
                self.data[data_set].location_scatter_plot = \
                    cdc_hosp_analysis.location_scatter_plot(clean_data)
                self.data[data_set].box_plot = \
                    cdc_hosp_analysis.location_box_plot(clean_data, color_pallet)
                self.data[data_set].bar_plot = \
                    cdc_hosp_analysis.sex_category_bar_plot(clean_data)
                self.data[data_set].stats = \
                    cdc_hosp_analysis.calc_stats(clean_data)
                self.data[data_set].pivot_plot = \
                    cdc_hosp_analysis.pivot_and_plot(clean_data)


class DataSet:
    def __init__(self):
        self.raw_data: pd.DataFrame = None
        self.clean_data: pd.DataFrame = None

        # csv data
        self.source_location: str = None
        self.save_location: str = None

        # api data
        self.api_source: str = None
        self.api_endpoint: str = None
        self.api_header: dict = None
        self.api_parameter_name: str = None
        self.api_parameters: str = None
        self.ingest_type: str = None

        # plot data
        self.overall_scatter_plot = None
        self.box_plot = None
        self.bar_plot = None
        self.stats = None
        self.pivot_plot = None


class AnalysisModule:
    pass


class CdcAnalysisModule(AnalysisModule):
    def overall_scatter_plot(self, input_data, color_pallet):
        overall_data = input_data[(input_data['date'] <= pd.Timestamp('2013-07-01')) &
                                  (input_data['AGE CATEGORY'] == 'Overall') &
                                  (input_data['SEX CATEGORY'] == 'Overall') &
                                  (input_data['RACE CATEGORY'] == 'Overall') &
                                  (input_data['CATCHMENT'] == 'Entire Network') &
                                  (input_data['NETWORK'] == 'FluSurv-NET')]

        fig, ax = plt.subplots(figsize=(8, 6))
        plt.xlabel('Date')
        plt.ylabel('Weekly Rate')
        plt.title('Overall Weekly Rate Over Time')
        ax.plot(overall_data['date'],
                overall_data['WEEKLY RATE'],
                color=color_pallet[0])
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.tight_layout()
        plt.title('Weekly US Influenza Hospitalizations Rate')
        plt.show()
        plt.close()
        return plt

    def location_scatter_plot(self, input_data):
        # Plot locations weekly rates over time
        location_plot = input_data[(input_data['AGE CATEGORY'] == 'Overall') &
                                   (input_data['SEX CATEGORY'] == 'Overall') &
                                   (input_data['RACE CATEGORY'] == 'Overall') &
                                   (input_data['CATCHMENT'] != 'Entire Network') &
                                   (input_data['NETWORK'] != 'FluSurv-NET')]
        grouped = location_plot.groupby('CATCHMENT')
        fig, ax = plt.subplots(figsize=(8, 6))
        i = 0
        locations_to_plot = [
            'California',
            'New York - Rochester',
            'New York - Albany',
            'Michigan',
            'Georga',
            'New Mexico',
            'Idaho'
        ]
        for location, subplot_data in grouped:
            if location in locations_to_plot:
                ax.plot(
                    subplot_data['date'],
                    subplot_data['WEEKLY RATE'],
                    label=location,
                    color=cm.rainbow(i * 3 / len(grouped))
                )
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
                ax.set_xlim(subplot_data['date'].min(), pd.Timestamp('2013-07-01'))
                ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
                i += 1
        ax.legend()
        plt.show()
        plt.close()
        return plt

    def location_box_plot(self, input_data, color_pallet):
        # Use seaborn to create a boxplot of the weekly rate by catchment
        sns.boxplot(x='CATCHMENT',
                    y='WEEKLY RATE',
                    data=input_data,
                    color=color_pallet[1])
        plt.xlabel('Catchment')
        plt.xticks(rotation=90)
        plt.ylabel('Weekly Rate')
        plt.title('Box Plot: Weekly Rate by Catchment')
        plt.tight_layout()
        plt.show()
        plt.close()
        return plt

    def sex_category_bar_plot(self, input_data):
        # Bar plot to show ratio between men and women
        bar_plot = input_data[(input_data['AGE CATEGORY'] == 'Overall') &
                              (input_data['RACE CATEGORY'] == 'Overall') &
                              (input_data['CATCHMENT'] == 'Entire Network') &
                              (input_data['NETWORK'] == 'FluSurv-NET')]
        sns.barplot(x='SEX CATEGORY',
                    y='WEEKLY RATE',
                    data=bar_plot)
        plt.xlabel('Sex Category')
        plt.xticks(rotation=90)
        plt.ylabel('Cumulative Rate')
        plt.title('Weekly Rate by Sex Category')
        plt.tight_layout()
        plt.show()
        return plt

    def calc_stats(self, input_data):
        # Calculate summary statistics
        description = input_data['WEEKLY RATE'].describe()
        print(description)

        # Group subplot_data by season and calculate rudimentary statistics
        mean = input_data.groupby(['AGE CATEGORY']).mean()['WEEKLY RATE']
        print("\n____MEAN____")
        print(mean)
        median = input_data.groupby(['AGE CATEGORY'])['WEEKLY RATE'].median()
        print("\n____MEDIAN____")
        print(median)

        stats = {
            'description': description,
            'mean': mean,
            'median': median
        }
        return stats

    def pivot_and_plot(self, input_data):
        # Create pivot table
        pivot_data = input_data[~((input_data['CATCHMENT'] != 'Entire Network')
                                  & (input_data["AGE CATEGORY"] == "Overall")
                                  & (input_data["SEX CATEGORY"] == "Overall")
                                  & (input_data["RACE CATEGORY"] == "Overall"))]
        pivot_table = pivot_data.pivot_table(
            values='WEEKLY RATE',
            index='AGE CATEGORY',
            columns='RACE CATEGORY')

        # Plot pivot table
        pivot_table.plot(kind='bar', stacked=True)
        plt.xlabel('Age Category')
        plt.xticks(rotation=90)
        plt.ylabel('Weekly Rate')
        plt.title('Weekly Rate by Age Category and Race Category')
        plt.tight_layout()
        plt.show()
        return plt
