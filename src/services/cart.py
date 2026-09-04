from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.db.models.cart_items import CartItem
from src.db.models.users import User
from src.db.models.carts import Cart


async def get_or_create_cart(
    db: AsyncSession,
    user: User
) -> Cart:
    query = (
        select(Cart)
        .options(
            selectinload(Cart.cart_items)
            .selectinload(CartItem.product)
        )
        .where(Cart.user_id == user.id)
    )

    result = await db.execute(query)

    cart = result.scalar_one_or_none()

    if cart is None:
        cart = Cart(user_id=user.id)
        db.add(cart)
        await db.flush()

    return cart
