from pydantic import BaseModel
from typing import Optional

class OrderStatusResponse(BaseModel):
    order_id: str
    status: str
    tracking_id: Optional[str]

    class Config:
        from_attributes = True

class TransitStatusResponse(BaseModel):
    tracking_id: str
    status: str
    location: str

    class Config:
        from_attributes = True