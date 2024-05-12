from fastapi import APIRouter
from typing import Optional, List

from src.earnings_utilities.earnings_aggregator import EarningsCalculator
from src.models.earnings_summary import EarningsSummarizer
router = APIRouter()


@router.post("/earnings-summary")
async def get_earnnings_summary(model: Optional[EarningsSummarizer] = None):
    if model is not None:
        model = model.model_dump()
    earnings_summary = EarningsCalculator().calc_earnings_summary(model)
    #return {"Beat": earnings_summary[1], "Missed": earnings_summary[0]}
    return earnings_summary