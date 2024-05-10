from fastapi import APIRouter
from typing import Optional, List

from src.earnings_utilities.earnings_aggregator import EarningsCalculator

router = APIRouter()


@router.get("/earnings_summary")
async def get_earnnings_summary():
    earnings_summary = EarningsCalculator().calc_earnings_summary()
    #return {"Beat": earnings_summary[1], "Missed": earnings_summary[0]}
    return earnings_summary
