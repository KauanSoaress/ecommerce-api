from pydantic import BaseModel, Field, ConfigDict


class CategoryCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="The name of the category"
    )


class CategoryUpdate(BaseModel):
    name: str | None = Field(
        None,
        min_length=2,
        max_length=100,
        description="The name of the category"
    )


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    slug: str
