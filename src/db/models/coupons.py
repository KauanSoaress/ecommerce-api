from src.db.base import Base
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column


class Coupon(Base):
    __tablename__ = "coupons"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(unique=True, nullable=False)
    discount: Mapped[float] = mapped_column(nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"Coupon(id={self.id!r}, code={self.code!r}, discount={self.discount!r}, expires_at={self.expires_at!r})"
