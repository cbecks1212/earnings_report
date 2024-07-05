from fastapi import APIRouter, Depends, HTTPException
from starlette import status
from typing import Optional
import pandas as pd
from ..auth.utils import get_current_user
from ..models.earnings_summary import EarningsSummarizer
from ..earnings_utilities.earnings_aggregator import EarningsCalculator
from ..earnings_utilities.common_functions import return_valid_symbol

router = APIRouter(tags=["Upcoming Earnings Announcements"],
                   dependencies=[Depends(get_current_user)])

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
    is_valid_symbol = return_valid_symbol(symbol)
    if not is_valid_symbol:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{symbol} is not a valid symbol")
    announcement = EarningsCalculator().get_earnings_announcement_symbol(symbol)
    return announcement