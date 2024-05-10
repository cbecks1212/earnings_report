from datetime import datetime

import numpy as np
import pandas as pd
import requests
#from src.config import settings
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("DEV_FIN_APIKEY")

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

    def calc_earnings_summary(self) -> dict:
        start_date, end_date = EarningsCalculator().calc_earning_start_end_date()

        resp = requests.get(
            f"https://financialmodelingprep.com/api/v3/earning_calendar?from={start_date}&to={end_date}&apikey={API_KEY}"
        )

        #df = pd.json_normalize(resp.json())
        """filtered_df = df.query("eps.notnull()", engine="python").query(
            "epsEstimated.notnull()", engine="python"
        )"""
        #filtered_df = df[(~df['eps'].isnull()) & (~df['epsEstimated'].isnull())]
        """filtered_df["beatEarnings"] = np.where(
            filtered_df["eps"] > filtered_df["epsEstimated"], 1, 0
        )"""
        #summary_dict = filtered_df["beatEarnings"].value_counts().to_dict()
        summary_dict = {"status_code" : resp.status_code}
        return summary_dict
