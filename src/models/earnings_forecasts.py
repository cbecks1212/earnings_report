from pydantic import BaseModel
from typing_extensions import Optional, List

class EarningsForecast(BaseModel):
    symbol: str
    data: Optional[List] = None
