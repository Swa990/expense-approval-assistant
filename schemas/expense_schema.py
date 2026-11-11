from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional


class ExpenseInput(BaseModel):
    employee_name: str
    employee_id: Optional[str] = None
    amount: Decimal = Field(gt=0)
    currency: str = "INR"
    category: str
    manager_approval: Optional[bool] = None
    description: Optional[str] = None