from datetime import datetime
from typing_extensions import Optional, List
import numpy as np
import pandas as pd
import requests
from datetime import timedelta
#from src.config import settings
from openai import OpenAI
from google.cloud import secretmanager
from functools import lru_cache
from io import BytesIO
import joblib
from .common_functions import return_stock_metadata, return_constituents

client = secretmanager.SecretManagerServiceClient()
project_id = "orbital-kit-400022"
secret_id = "DEV_FIN_APIKEY"
open_ai_id = "OPENAI_API_KEY"

# Build the secret name
secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
open_ai_name = f"projects/{project_id}/secrets/{open_ai_id}/versions/latest"

# Access the secret
response = client.access_secret_version(request={"name": secret_name})
payload = response.payload.data.decode("UTF-8")

ai_reponse = client.access_secret_version(request={"name": open_ai_name})
openai_api_key = ai_reponse.payload.data.decode("UTF-8")

class MLUtils:
    def load_eps_feature_data(self, ticker):
        fin_growth_json = requests.get(f"https://financialmodelingprep.com/api/v3/financial-growth/{ticker}?period=quarter&apikey={payload}").json()[0]

        ratio_json = requests.get(f"https://financialmodelingprep.com/api/v3/ratios/{ticker}?period=quarter&apikey={payload}").json()[0]

        earnings_json = requests.get(f"https://financialmodelingprep.com/api/v3/historical/earning_calendar/{ticker}?apikey={payload}").json()

        growth_df = pd.json_normalize(fin_growth_json)
        ratio_df = pd.json_normalize(ratio_json)
        earnings_df = pd.json_normalize(earnings_json)
        merged_df = pd.merge(growth_df, ratio_df, on=["symbol", "date", "calendarYear", "period"])

        merged_df = merged_df.merge(earnings_df, left_on=["symbol", "date"], right_on=["symbol", "fiscalDateEnding"])

        merged_df.sort_values(by=["symbol", "date_x"], ascending=True, inplace=True)
        #merged_df.fillna(-1000000000, inplace=True)
        numeric_df = merged_df.select_dtypes(include=np.number)
        numeric_df = numeric_df.apply(lambda x: x.fillna(x.median()), axis=0)

        numeric_df = numeric_df.drop(columns=['eps', 'revenue'])

        X = numeric_df.to_numpy()

        return X
    
    @staticmethod
    @lru_cache(maxsize=1)
    def load_model(self, binary_data):
        model = joblib.load(BytesIO(binary_data))
        return model