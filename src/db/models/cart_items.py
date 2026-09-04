from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.db.models.carts import Cart
    from src.db.models.products import Product

from src.db.base import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class CartItem(Base):
    __tablename__ = "cart_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False
    )
    quantity: Mapped[int] = mapped_column(nullable=False)

    cart: Mapped["Cart"] = relationship(back_populates="cart_items", passive_deletes=True)
    product: Mapped["Product"] = relationship(back_populates="cart_items")

    def __repr__(self) -> str:
        return f"CartItem(id={self.id!r}, cart_id={self.cart_id!r}, product_id={self.product_id!r}, quantity={self.quantity!r})"
