import pandas as pd
import requests
import numpy as np
from google.cloud import secretmanager

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


def return_stock_metadata():
    metadata_df = pd.read_csv("https://raw.githubusercontent.com/cbecks1212/cb_datasets/main/stock_metadata.csv", sep=",")
    return metadata_df

def return_constituents(index: str) -> list:
    if index == "S&P 500":
        constituents_dict = requests.get(f"https://financialmodelingprep.com/api/v3/sp500_constituent?apikey={payload}").json()
    elif index == "NASDAQ 100":
        constituents_dict = requests.get(f"https://financialmodelingprep.com/api/v3/nasdaq_constituent?apikey={payload}").json()

    constituents = [symbol["symbol"] for symbol in constituents_dict]
    
    return constituents



