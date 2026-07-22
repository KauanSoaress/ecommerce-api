from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict


class CartItemCreate(BaseModel):
    product_id: int = Field(
        ...,
        description="The ID of the product associated with the cart item"
    )
    quantity: int = Field(
        ...,
        gt=0,
        description="The quantity of the product in the cart"
    )


class CartItemUpdate(BaseModel):
    quantity: int | None = Field(
        None,
        gt=0,
        description="The quantity of the product in the cart"
    )


class CartItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cart_id: int
    product_id: int
    quantity: int
    subtotal: Decimal