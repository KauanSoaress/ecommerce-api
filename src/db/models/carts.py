from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.db.models.users import User
    from src.db.models.cart_items import CartItem

from src.db.base import Base
from datetime import datetime
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Cart(Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True
    )
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="cart", passive_deletes=True)
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="cart", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"Cart(id={self.id!r}, user_id={self.user_id!r}, created_at={self.created_at!r})"