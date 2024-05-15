from fastapi import APIRouter
from typing import Optional, List

from src.earnings_utilities.earnings_aggregator import EarningsCalculator
from src.models.earnings_summary import EarningsSummarizer, PeerEarnings
router = APIRouter()


@router.post("/earnings-summary", summary="Provides a count of companies that beat or missed their earnings. There is an option to filter counts by industry and index.")
async def get_earnings_summary(model: Optional[EarningsSummarizer] = None):
    if model is not None:
        model = model.model_dump()
    earnings_summary = EarningsCalculator().calc_earnings_summary(model)
    #return {"Beat": earnings_summary[1], "Missed": earnings_summary[0]}
    return earnings_summary

@router.post("/earnings-by-industry", summary="Provides a breakout of earnings by industry. There is an also an option to refine this further by filtering by companies in the S&P 500 and/or NASDAQ.")
async def industry_earnings_summary(model: Optional[EarningsSummarizer] = None):
    if model is not None:
        model = model.model_dump()
    company_summaries = EarningsCalculator().summarize_company_earnings(model)
    return company_summaries

@router.post("/company-earnings-analysis")
async def company_earnings_analysis(symbol: str):
    company_analysis = EarningsCalculator().analyze_company_earnings_report(symbol)
    return company_analysis

@router.post("/peer-earnings-analysis")
async def peer_earnings_analysis(symbol: str, peer_model: Optional[PeerEarnings] = None):
    if peer_model is not None:
        peer_model = peer_model.model_dump()
        peer_analysis = EarningsCalculator().peer_analysis_earnings(symbol, peer_model)
    else:
        peer_analysis = EarningsCalculator().peer_analysis_earnings(symbol)
    return peer_analysis