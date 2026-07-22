from datetime import datetime
from pydantic import BaseModel, ConfigDict
from src.schemas.cart_item import CartItemOut


class CartOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    created_at: datetime
    items: list["CartItemOut"] = []
    total_value: float = 0.0
