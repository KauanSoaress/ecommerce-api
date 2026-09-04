from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from src.schemas.cart_item import CartItemOut


class CartOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    created_at: datetime
    cart_items: list[CartItemOut] = Field(default_factory=list)
    total_value: float = 0.0
