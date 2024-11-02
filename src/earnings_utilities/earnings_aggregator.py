from datetime import datetime
from typing_extensions import Optional, List
import numpy as np
import pandas as pd
import requests
from datetime import timedelta
#from src.config import settings
from openai import OpenAI
from google.cloud import secretmanager
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


class EarningsCalculator:
    def calc_earning_start_end_date(self, month=None):
        todays_date = datetime.now().date()
        if month is None:
            month = todays_date.month
        if month in [4, 5, 6]:
            start_month = "03"
            start_day = "31"
            end_month = "06"
            end_day = "30"
        elif month in [7, 8, 9]:
            start_month = "06"
            start_day = "30"
            end_month = "09"
            end_day = "30"
        elif month in [10, 11, 12]:
            start_month = "09"
            start_day = "30"
            end_month = "12"
            end_day = "31"
        else:
            start_month = "12"
            start_day = "31"
            end_month = "03"
            end_day = "31"

        earning_start_day = f"{todays_date.year}-{start_month}-{start_day}"
        earning_end_day = f"{todays_date.year}-{end_month}-{end_day}"
        start_day = datetime.strptime(earning_start_day, '%Y-%m-%d') + timedelta(days=10)
        if start_day.year != todays_date.year:
            start_day = start_day - timedelta(days=365)
        start_day = start_day.strftime("%Y-%m-%d")
        return start_day, earning_end_day
    
    def get_price_data(self, ticker):
        json_prices = requests.get(f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?serietype=line&apikey={payload}").json()
        df = pd.json_normalize(json_prices, record_path='historical')
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values(by='date')
        return df
    
    def calc_stock_performance(self, ticker) -> pd.DataFrame:
        performance = requests.get(f"https://financialmodelingprep.com/api/v3/stock-price-change/{ticker}?apikey={payload}").json()
        df = pd.json_normalize(performance)
        return df
    
    

    def calc_earnings_summary(self, params: dict) -> dict:
        start_date, end_date = EarningsCalculator().calc_earning_start_end_date()
        print("Params")
        print(params)


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

            if params["earnings_start_date"] is not None:
                start_date = params["earnings_start_date"]
        
            if params["earnings_end_date"] is not None:
                end_date = params["earnings_end_date"]

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

        if "Missed" not in summary_dict:
            summary_dict.update({"Missed" : 0})
        
        if "Beat" not in summary_dict:
            summary_dict.update({"Beat" : 0})

        summary_dict.update({"earnings_start_date": start_date, "earnings_end_date" : end_date})    
        
        return summary_dict
    
    def calc_price_perf_after_earnings(self, ticker: str, date: str) -> float:
        #date = datetime.strptime(date, "%Y-%m-%d")
        try:
            price_df = EarningsCalculator().get_price_data(ticker)
            price_df['date'] = price_df['date'].dt.strftime("%Y-%m-%d")
        except:
            price_df = None
        if price_df is not None:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            if date_obj.weekday() == 0:
                prior_date =   date_obj - timedelta(days=3)
            else:
                prior_date = date_obj - timedelta(days=1)
            prior_date = prior_date.strftime("%Y-%m-%d")
            dates = [prior_date, date]
            filtered_price_df = price_df.query("date in @dates")
            filtered_price_df['priceChangePostEarnings'] = filtered_price_df['close'].pct_change().dropna()
            return str(filtered_price_df['priceChangePostEarnings'].iloc[-1])
        else:
            return "NULL"
        
    def get_company_earnings(self, symbol: str) -> pd.DataFrame:
        start_date, end_date = EarningsCalculator().calc_earning_start_end_date()

        resp = requests.get(
            f"https://financialmodelingprep.com/api/v3/earning_calendar?from={start_date}&to={end_date}&apikey={payload}"
        )

        df = pd.json_normalize(resp.json())
        filtered_df = df.query("eps.notnull()", engine="python").query(
            "epsEstimated.notnull()", engine="python"
        ).query("symbol == @symbol")

        if not filtered_df.empty:
            filtered_df["beatEarnings"] = np.where(filtered_df["eps"] > filtered_df["epsEstimated"], "Beat", "Missed"
        )
            filtered_df['performanceAfterEarnings'] = filtered_df.apply(lambda x: EarningsCalculator().calc_price_perf_after_earnings(x.symbol, x.date), axis=1)

            price_perf_df = EarningsCalculator().calc_stock_performance(symbol)
            filtered_df = filtered_df.merge(price_perf_df, on="symbol")

            return filtered_df
        else:
            return pd.DataFrame()
    
    def summarize_company_earnings(self, params: dict) -> dict:
        start_date, end_date = EarningsCalculator().calc_earning_start_end_date()

        resp = requests.get(
            f"https://financialmodelingprep.com/api/v3/earning_calendar?from={start_date}&to={end_date}&apikey={payload}"
        )

        df = pd.json_normalize(resp.json())

        filtered_df = df.query("eps.notnull()", engine="python").query(
            "epsEstimated.notnull()", engine="python"
        )

        metadata_df = pd.read_csv("https://raw.githubusercontent.com/cbecks1212/cb_datasets/main/stock_metadata.csv", sep=",")

        if params is not None:
            print("params are running")
            industry = params["industry"]
            indexes = params["indexes"]
            
            if industry is not None:
                metadata_df = metadata_df.query("industry in @industry")
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
            
            if params["earnings_start_date"] is not None:
                start_date = params["earnings_start_date"]
        
            if params["earnings_end_date"] is not None:
                end_date = params["earnings_end_date"]

        filtered_df["beatEarnings"] = np.where(
            filtered_df["eps"] > filtered_df["epsEstimated"], "Beat", "Missed"
        )

        filtered_df = filtered_df.merge(metadata_df, on="symbol")[["symbol", "industry", "beatEarnings", "date"]].fillna("NULL")
        
        #filtered_df['price_change_after_earnings'] = filtered_df.apply(lambda x: EarningsCalculator().calc_price_perf_after_earnings(x.symbol, x.date), axis=1)

        summary_dict = filtered_df.to_dict(orient="records")
        return summary_dict
    
    def generate_ai_text(self, ticker: str):
        earnings_dates_resp = requests.get(f"https://financialmodelingprep.com/api/v4/earning_call_transcript?symbol={ticker}&apikey={payload}").json()
        if len(earnings_dates_resp) > 0:
            quarter = earnings_dates_resp[0][0]
            year = earnings_dates_resp[0][1]

            resp = requests.get(f"https://financialmodelingprep.com/api/v3/earning_call_transcript/{ticker}?year={year}&quarter={quarter}&apikey={payload}").json()

            if len(resp) > 0:
                client = OpenAI(api_key=openai_api_key)
                transcript = resp[0]["content"]
                transcript = transcript[0:10000]
                chat_obj = client.chat.completions.create(messages=[
                {"role": "user", "content": f"Analyze and summarize {ticker}'s following earnings transcript: {transcript}"}
                ],
                model="gpt-4",
                temperature=1,
                max_tokens=500)

                ai_text = chat_obj.choices[0].message.content
            else:
                ai_text = f"{ticker}'s earnings transcript not found"
        else:
            ai_text = f"{ticker}'s earnings transcript not found"
        

        return ai_text
    
    def analyze_company_earnings_report(self, symbol: str) -> dict:
        earnings_agg = EarningsCalculator()
        start_date_str, end_date_str = earnings_agg.calc_earning_start_end_date()
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

        today_date = datetime.now()

        """resp = requests.get(
            f"https://financialmodelingprep.com/api/v3/historical/earning_calendar/{symbol}?apikey={payload}"
        )"""
        resp = requests.get(f"https://financialmodelingprep.com/api/v3/earning_calendar?from={start_date_str}&to={end_date_str}&apikey=3539c122c2e660ee9cdbd32cc28c0e04").json()
        filtered_json = [obj for obj in resp if obj['symbol'] == symbol]
        print(filtered_json)


        df = pd.json_normalize(filtered_json)
        df['date'] = pd.to_datetime(df['date'])
        ticker_df = df.query("date >= @start_date and date < @end_date and symbol == @symbol")

        if not ticker_df.empty:
            if ticker_df['date'].iloc[0] <= today_date:
                ticker_df["beatEarnings"] = np.where(
                ticker_df["eps"] > ticker_df["epsEstimated"], "Beat", "Missed")
                ticker_df["performanceAfterEarnings"] = ticker_df.apply(lambda x: earnings_agg.calc_price_perf_after_earnings(x.symbol, datetime.strftime(x.date, "%Y-%m-%d")), axis=1)
                earnings_summary_text = earnings_agg.generate_ai_text(symbol)
                summary_dict = ticker_df[["date", "symbol", "eps", "epsEstimated", "beatEarnings", "performanceAfterEarnings"]].to_dict(orient="records")
                summary_dict[0].update({"transcriptSummary" : earnings_summary_text})
            else:
                """earnings_date = datetime.strftime(ticker_df['date'].iloc[0], "%Y-%m-%d")"""
                earnings_date = earnings_agg.get_earnings_announcement_symbol(symbol)["announcement_date"]
                summary_dict = {"symbol" : symbol, "earnings_date": f"{symbol} will announce its earnings on {earnings_date}"}
        else:
            summary_dict = {"msg" : f"{symbol}'s earnings date has yet to be confirmed"}
        return summary_dict
    
    def peer_analysis_earnings(self, ticker: str, peer_list: Optional[List] = None):
        master_peer_df = pd.DataFrame()
        if peer_list is None:
            ticker_peers_req = requests.get(f"https://financialmodelingprep.com/api/v4/stock_peers?symbol={ticker}&apikey={payload}").json()
            ticker_peers = ticker_peers_req[0]['peersList']
        else:
            ticker_peers = peer_list

        ticker_df = EarningsCalculator().get_company_earnings(ticker)
        if not ticker_df.empty:
            ticker_beat_earnings = ticker_df["beatEarnings"].iloc[0]
        else:
            ticker_beat_earnings = f"{ticker} has not announced earnings yet"


        for peer in ticker_peers:
            peer_df = EarningsCalculator().get_company_earnings(peer)
            master_peer_df = pd.concat([master_peer_df, peer_df])
        if 'beatEarnings' in master_peer_df.columns.tolist():    
            peer_counts = master_peer_df['beatEarnings'].value_counts()
        try:
            peer_beat = str(peer_counts["Beat"])
        except:
            peer_beat = "0"
        
        try:
            peer_missed = str(peer_counts["Missed"])
        except:
            peer_missed = "0"

        summary_dict = {ticker: ticker_beat_earnings, "peerBeatEarnings" : peer_beat, "peerMissedEarnings" : peer_missed}
        master_peer_df = pd.concat([master_peer_df, ticker_df])
        summary_dict.update({"data" : master_peer_df[["symbol", "date", "eps", "epsEstimated", "beatEarnings", "performanceAfterEarnings", "1M", "3M", "6M", "1Y", "ytd"]].to_dict(orient="records")})



        return summary_dict
    
    def get_earnings_announcements(self, request_data):
        metadata_df = return_stock_metadata()
        indexes = None
        industries = None
        start_date, end_date = EarningsCalculator().calc_earning_start_end_date()

        if request_data is not None:
            indexes = request_data["indexes"]
            industries = request_data["industry"]

            if request_data["earnings_start_date"] is not None:
                start_date = request_data["earnings_start_date"]
        
            if request_data["earnings_end_date"] is not None:
                end_date = request_data["earnings_end_date"]
        todays_date = datetime.now().strftime("%Y-%m-%d")
        df = pd.json_normalize(requests.get(f"https://financialmodelingprep.com/api/v3/earning_calendar?from={todays_date}&to={end_date}&apikey={payload}").json())
        df["date"] = pd.to_datetime(df["date"])
        df.sort_values(by="date", ascending=True, inplace=True)

        if indexes is not None:
            sp_constituents = []
            nasdaq_constituents = []

            if "S&P 500" in indexes:
                sp_constituents = return_constituents("S&P 500")
            if "NASDAQ 100" in indexes:
                nasdaq_constituents = return_constituents("NASDAQ 100")
            
            constituents = sp_constituents + nasdaq_constituents
            constituents = list(set(constituents))

            df = df.query("symbol in @constituents")
        
        if industries is not None:
            metadata_df = metadata_df.query("industry in @industries")

        date_dict = {"earnings_start_date" : start_date, "earnings_end_date" : end_date}    
        
        records = pd.merge(df, metadata_df, on="symbol").fillna("NULL").to_dict(orient="records")
        
        records.insert(0, date_dict)

        return records
    
    def get_earnings_announcement_symbol(self, symbol):
        start_date, end_date = EarningsCalculator().calc_earning_start_end_date()

        df = pd.json_normalize(requests.get(f"https://financialmodelingprep.com/api/v3/earning_calendar?from={start_date}&to={end_date}&apikey={payload}").json())

        df = df.query("symbol == @symbol")

        announcement_date = df['date'].iloc[0]

        return {"announcement_date" : announcement_date}
    
    def get_closest_date(self, ticker):
        json = requests.get(f"https://financialmodelingprep.com/api/v3/historical/earning_calendar/{ticker}?apikey={payload}").json()[0:6]
        todays_date = datetime.now().date()
        year = todays_date.year
        date_list = []

        for i in range(0, len(json)):
            date_str = json[i]['date']
            json_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            if json_date > todays_date and json_date.year == year:
                date_list.append(json_date)
    
        next_date = min(date_list)
        return next_date

        

        
    

