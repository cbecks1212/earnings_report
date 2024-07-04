from pydantic import BaseModel
from typing_extensions import Optional, List

class EarningsSummarizer(BaseModel):
    industry: Optional[List] = None
    indexes: Optional[List] = None
    earnings_start_date: Optional[str] = None
    earnings_end_date: Optional[str] = None

class PeerEarnings(BaseModel):
    peers: Optional[List] = None
