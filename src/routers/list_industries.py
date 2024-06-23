from fastapi import APIRouter, Depends
from typing import Optional
import pandas as pd
from ..auth.utils import get_current_user
from ..models.earnings_summary import EarningsSummarizer
from ..earnings_utilities.earnings_aggregator import EarningsCalculator

router = APIRouter(tags=["Earnings Announcements and Helpers"],
                   dependencies=[Depends(get_current_user)])

@router.get("/list-industries")
def get_industries():
    df = pd.read_csv("https://raw.githubusercontent.com/cbecks1212/cb_datasets/main/industry_dataset.csv")
    industries = df['industry'].values.tolist()
    return {"industries" : industries}

@router.get("/list-indexes")
def get_indexes():
    
    return {"indexes" : ["S&P 500", "NASDAQ 100"]}

@router.post("/upcoming-announcements")
def get_announcement_dates(model: Optional[EarningsSummarizer] = None):
    if model is not None:
        data = model.model_dump()
    else:
        data = None
    announcements = EarningsCalculator().get_earnings_announcements(data)
    return announcements

@router.get("/upcoming-announcements/{symbol}")
def get_announcement_symbol(symbol: str):
    announcement = EarningsCalculator().get_earnings_announcement_symbol(symbol)
    return announcement


