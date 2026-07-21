from fastapi import Form
from decimal import Decimal
from pydantic import BaseModel, Field, HttpUrl, ConfigDict

class ProductCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=100,
        description="The name of the product"
    )
    description: str | None = Field(
        None,
        max_length=200,
        description="A brief description of the product"
    )
    price: Decimal = Field(
        ...,
        gt=0,
        description="The price of the product, must be greater than 0"
    )
    stock: int = Field(
        ...,
        gt=0,
        description="The quantity of the product in stock"
    )
    category_id: int = Field(
        ...,
        gt=0,
        description="The ID of the category this product belongs to"
    )

    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        description: str | None = Form(None),
        price: Decimal = Form(...),
        stock: int = Form(...),
        category_id: int = Form(...),
    ):
        return cls(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category_id=category_id,
        )

class ProductUpdate(BaseModel):
    name: str | None = Field(
        None,
        min_length=2,
        max_length=100,
        description="The name of the product"
    )
    description: str | None = Field(
        None,
        max_length=200,
        description="A brief description of the product"
    )
    price: float | None = Field(
        None,
        gt=0,
        description="The price of the product, must be greater than 0"
    )
    stock: int | None = Field(
        None,
        gt=0,
        description="The quantity of the product in stock"
    )
    category_id: int | None = Field(
        None,
        gt=0,
        description="The ID of the category this product belongs to"
    )
    image_url: HttpUrl | None = Field(
        None,
        description="URL of the product image"
    )

class ProductStockUpdate(BaseModel):
    stock: int = Field(
        ...,
        ge=0,
        description="The quantity of the product in stock"
    )

class ProductOut(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    category_id: int
    image_url: HttpUrl | None

    model_config = ConfigDict(from_attributes=True)