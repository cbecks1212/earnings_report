from fastapi import APIRouter, Depends
from typing import Optional
import pandas as pd
from ..auth.utils import get_current_user
from ..models.earnings_summary import EarningsSummarizer
from ..earnings_utilities.earnings_aggregator import EarningsCalculator

router = APIRouter(tags=["Helpers"],
                   dependencies=[Depends(get_current_user)])

@router.get("/list-industries", summary="Provides a list of industries to search from")
async def get_industries():
    df = pd.read_csv("https://raw.githubusercontent.com/cbecks1212/cb_datasets/main/industry_dataset.csv")
    industries = df['industry'].values.tolist()
    return {"industries" : industries}

@router.get("/list-indexes", summary="Provides a list of indices to search from. S&P 500 and NASDAQ 100 are currently supported.")
async def get_indexes():
    
    return {"indexes" : ["S&P 500", "NASDAQ 100"]}

@router.get("/list-earnings-season-dates", summary="Provides a list of Earning Season start and end dates for the current year")
async def get_earning_season_dates():
    date_dict = {}
    q1_start_date, q1_end_date = EarningsCalculator().calc_earning_start_end_date(1)
    q2_start_date, q2_end_date = EarningsCalculator().calc_earning_start_end_date(4)
    q3_start_date, q3_end_date = EarningsCalculator().calc_earning_start_end_date(7)
    q4_start_date, q4_end_date = EarningsCalculator().calc_earning_start_end_date(10)

    date_dict.update({"Q1" : {"start" : q1_start_date, "end": q1_end_date}})
    date_dict.update({"Q2" : {"start" : q2_start_date, "end" : q2_end_date}})
    date_dict.update({"Q3" : {"start" : q3_start_date, "end" : q3_end_date}})
    date_dict.update({"Q4" : {"start" : q4_start_date, "end" : q4_end_date}})

    return date_dict




