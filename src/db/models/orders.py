from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.db.models.order_items import OrderItem
    from src.db.models.users import User

from sqlalchemy import Enum
from src.db.base import Base
from datetime import datetime
from sqlalchemy import ForeignKey, func
from src.db.enums.order_status import OrderStatus
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("auth_users.id", ondelete="CASCADE"),
        nullable=False
    )
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        nullable=False,
        default=OrderStatus.PENDING,
    )
    total: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(nullable=False, server_default=func.now())

    order_items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
    user: Mapped["User"] = relationship(
        back_populates="orders"
    )

    def __repr__(self) -> str:
        return f"Order(id={self.id!r}, user_id={self.user_id!r}, status={self.status!r}, total={self.total!r}, created_at={self.created_at!r})"