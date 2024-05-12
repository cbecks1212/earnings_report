from fastapi import APIRouter
import pandas as pd

router = APIRouter()

@router.get("/list-industries")
def get_industries():
    df = pd.read_csv("https://raw.githubusercontent.com/cbecks1212/cb_datasets/main/industry_dataset.csv")
    industries = df['industry'].values.tolist()
    return {"industries" : industries}

@router.get("/list-indexes")
def get_indexes():
    
    return {"indexes" : ["S&P 500", "NASDAQ 100"]}