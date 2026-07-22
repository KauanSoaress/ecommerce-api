from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.db.models.categories import Category
    from src.db.models.cart_items import CartItem
    from src.db.models.order_items import OrderItem

from src.db.base import Base
from datetime import datetime
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    price: Mapped[float] = mapped_column(nullable=False)
    stock: Mapped[int] = mapped_column(nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False
    )
    image_url: Mapped[str] = mapped_column(nullable=False)
    image_public_id: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    category: Mapped["Category"] = relationship("Category", back_populates="products")
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="product")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="product")

    def __repr__(self) -> str:
        return f"Product(id={self.id!r}, name={self.name!r}, description={self.description!r}, price={self.price!r}, stock={self.stock!r}, category_id={self.category_id!r}, image_url={self.image_url!r}, created_at={self.created_at!r})"