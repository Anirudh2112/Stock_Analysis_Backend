from pydantic import BaseModel
from datetime import date
from typing import Optional

class AnalysisRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    volume_threshold: float = 200.0
    price_threshold: float = 2.0
    holding_period: int = 10