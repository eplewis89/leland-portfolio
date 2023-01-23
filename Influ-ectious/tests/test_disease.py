import os

import pandas as pd
import pytest

from influectious.disease import Disease


class TestClass:
    @pytest.fixture
    def disease(self):
        temp = Disease("Influenza")
        temp.data["cdc_hospitalization_rates"].source_location = \
            "Data" \
            "/CDC_FluView" \
            "/Hospitalizations" \
            "/Hospitalization_Rates" \
            "/test_data.csv"
        return temp

    def test_ingest(self, disease):
        assert disease.data["cdc_hospitalization_rates"] is not None
        assert disease.data["cdc_hospitalization_rates"].raw_data is None
        disease.ingest_data('csv')
        assert os.path.isfile(disease.data["cdc_hospitalization_rates"].save_location)
        assert disease.data['cdc_hospitalization_rates'].raw_data.columns.tolist() == \
               [
                   'CATCHMENT',
                   'NETWORK',
                   'YEAR',
                   'MMWR-YEAR',
                   'MMWR-WEEK',
                   'AGE CATEGORY',
                   'SEX CATEGORY',
                   'RACE CATEGORY',
                   'CUMULATIVE RATE',
                   'WEEKLY RATE '
               ]

    def test_clean(self, disease):
        disease.ingest_data('csv')
        assert disease.data["cdc_hospitalization_rates"].clean_data is None
        disease.clean_up_data()
        assert disease.data['cdc_hospitalization_rates'].clean_data.columns.tolist() == \
               [
                   'CATCHMENT',
                   'NETWORK',
                   'MMWR-YEAR',
                   'MMWR-WEEK',
                   'AGE CATEGORY',
                   'SEX CATEGORY',
                   'RACE CATEGORY',
                   'CUMULATIVE RATE',
                   'WEEKLY RATE'
               ]
