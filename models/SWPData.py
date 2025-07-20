from pydantic import BaseModel
from typing import Optional

class Data(BaseModel):
    corpus: float
    future_value: float
    reserve_corpus: float
    monthly_swp: float
    swp_schedule: list[tuple]


class SWPData(BaseModel):
    current_scenario: Optional[Data]
    target_scenario: Optional[Data]
