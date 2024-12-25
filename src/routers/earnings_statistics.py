from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from typing import Optional, List

from src.earnings_utilities.earnings_aggregator import EarningsCalculator
from src.earnings_utilities.common_functions import return_valid_symbol
from src.models.earnings_summary import EarningsSummarizer, PeerEarnings
from ..auth.utils import get_current_user

router = APIRouter(tags=["Earnings Statistics"],
                   dependencies=[Depends(get_current_user)])


@router.post("/earnings-summary", summary="Provides a count of companies that beat or missed their earnings. There is an option to filter counts by industry and index in the JSON body of the request.")
async def get_earnings_summary(model: Optional[EarningsSummarizer] = None):
    if model is not None:
        model = model.model_dump()
    earnings_summary = EarningsCalculator().calc_earnings_summary(model)
    #return {"Beat": earnings_summary[1], "Missed": earnings_summary[0]}
    return earnings_summary

@router.post("/earnings-breakout", summary="Provides a breakout of earnings, detailing actual EPS vs estimated EPS. There is an also an option to refine this further by filtering by companies in the S&P 500 and/or NASDAQ.")
async def industry_earnings_summary(model: Optional[EarningsSummarizer] = None):
    if model is not None:
        model = model.model_dump()
    company_summaries = EarningsCalculator().summarize_company_earnings(model)
    return company_summaries

@router.post("/company-earnings-analysis", summary="Returns an analysis of a company's earnings call.")
async def company_earnings_analysis(symbol: str):
    is_valid_symbol = return_valid_symbol(symbol)
    calc = EarningsCalculator()
    if not is_valid_symbol:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{symbol} is not a valid symbol")
    company_analysis = await calc.analyze_company_earnings_report(symbol)
    return company_analysis

@router.post("/peer-earnings-analysis", summary="Provides a comparison between a symbol and its peers. There is an option to customize the peer list via the JSON body of the request.")
async def peer_earnings_analysis(symbol: str, peer_model: Optional[PeerEarnings] = None):
    is_valid_symbol = return_valid_symbol(symbol)
    if not is_valid_symbol:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{symbol} is not a valid symbol")
    
    if peer_model is not None:
        peer_model = peer_model.model_dump()
        peer_analysis = EarningsCalculator().peer_analysis_earnings(symbol, peer_model)
    else:
        peer_analysis = EarningsCalculator().peer_analysis_earnings(symbol)
    return peer_analysis

@router.get("/price-after-earnings", status_code=200)
async def get_price_after_earnings(symbol: str):
    earnings_calc = EarningsCalculator()
    ticker_earnings_date = earnings_calc.get_earnings_announcement_symbol(symbol)['announcement_date']
    price_perf = EarningsCalculator().calc_price_perf_after_earnings(symbol, ticker_earnings_date)
    return {"symbol" : symbol, "earnings_date" : ticker_earnings_date, "stock_price_performance_after_earnings" : price_perf}

@router.get("/price-after-earnings-timeseries", status_code=200)
async def get_price_after_earnings_timeseries(symbol: str):
    earnings_calc = EarningsCalculator()
    historical_earnings_df = earnings_calc.get_earnings_calendar(symbol)
    historical_earnings_df['price_change_after_earnings'] = historical_earnings_df.apply(lambda x: earnings_calc.calc_price_perf_after_earnings(x.symbol, x.date.strftime("%F")), axis=1)
    dict_ = historical_earnings_df[['date', 'symbol', 'price_change_after_earnings']].to_dict(orient="records")
    return dict_