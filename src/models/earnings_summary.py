from pydantic import BaseModel
from typing_extensions import Optional, List

class EarningsSummarizer(BaseModel):
    industry: Optional[List] = None
    indexes: Optional[List] = None
