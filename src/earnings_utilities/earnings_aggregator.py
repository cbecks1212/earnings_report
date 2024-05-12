from datetime import datetime

import numpy as np
import pandas as pd
import requests
#from src.config import settings
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
project_id = "orbital-kit-400022"
secret_id = "DEV_FIN_APIKEY"

# Build the secret name
secret_name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"

# Access the secret
response = client.access_secret_version(request={"name": secret_name})
payload = response.payload.data.decode("UTF-8")

class EarningsCalculator:
    def calc_earning_start_end_date(self):
        todays_date = datetime.now().date()
        month = todays_date.month
        if month in [3, 4, 5]:
            start_month = "03"
            start_day = "31"
            end_month = "06"
            end_day = "30"
        elif month in [6, 7, 8]:
            start_month = "06"
            start_day = "30"
            end_month = "09"
            end_day = "30"
        elif month in [9, 10, 11, 12]:
            start_month = "09"
            start_day = "30"
            end_month = "12"
            end_day = "31"

        earning_start_day = f"{todays_date.year}-{start_month}-{start_day}"
        earning_end_day = f"{todays_date.year}-{end_month}-{end_day}"
        return earning_start_day, earning_end_day
    
    

    def calc_earnings_summary(self, params: dict) -> dict:
        start_date, end_date = EarningsCalculator().calc_earning_start_end_date()

        resp = requests.get(
            f"https://financialmodelingprep.com/api/v3/earning_calendar?from={start_date}&to={end_date}&apikey={payload}"
        )

        df = pd.json_normalize(resp.json())
        filtered_df = df.query("eps.notnull()", engine="python").query(
            "epsEstimated.notnull()", engine="python"
        )

        if params is not None:
            print("params are running")
            metadata_df = pd.read_csv("https://raw.githubusercontent.com/cbecks1212/cb_datasets/main/stock_metadata.csv", sep=",")
            industry = params["industry"]
            indexes = params["indexes"]
            
            if industry is not None:
                metadata_df = metadata_df.query("industry in @industry")
                filtered_df = filtered_df.merge(metadata_df, on="symbol")
            if indexes is not None:
                sp_constituents = requests.get(f"https://financialmodelingprep.com/api/v3/sp500_constituent?apikey={payload}").json()
                sp_tickers = pd.json_normalize(sp_constituents)['symbol'].values.tolist()
                nasdaq = requests.get(f"https://financialmodelingprep.com/api/v3/nasdaq_constituent?apikey={payload}").json()
                nasdaq_tickers = pd.json_normalize(nasdaq)["symbol"].values.tolist()
                if "S&P 500" in indexes and "NASDAQ 100" in indexes:
                    combined_tickers = sp_tickers + nasdaq_tickers
                    filtered_df = filtered_df.query("symbol in @combined_tickers")
                elif "S&P 500" in indexes:
                    filtered_df = filtered_df.query("symbol in @sp_tickers")
                elif "NASDAQ 100" in indexes:
                    filtered_df = filtered_df.query("symbol in @nasdaq_tickers")

        else:
            metadata_df = None

        filtered_df["beatEarnings"] = np.where(
            filtered_df["eps"] > filtered_df["epsEstimated"], "Beat", "Missed"
        )
        summary_dict = filtered_df["beatEarnings"].value_counts().to_dict()
        #summary_dict = {"Beat" : summary_dict["Beat"], "Missed": summary_dict["Missed"]}
        if metadata_df is not None:
            if industry is not None:
                industry_counts = filtered_df.groupby("industry")["beatEarnings"].value_counts().reset_index().to_dict(orient='records')
                summary_dict.update({"industry_counts" : industry_counts})
        
        return summary_dict
