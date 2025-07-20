from pydantic import BaseModel
from typing import Optional

class UserData(BaseModel):
    current_age: int
    expected_retirement_age: int
    expected_retirement_expenses: float
    current_retirement_corpus: float
    retirement_sip: float