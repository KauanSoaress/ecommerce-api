from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_db, get_current_user
from src.services.cart import get_or_create_cart
from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.cart import CartOut
from src.schemas.cart_item import CartItemCreate, CartItemOut

from src.db.models.users import User
from src.db.models.products import Product
from src.db.models.cart_items import CartItem

router = APIRouter(prefix='/cart', tags=["cart"])

@router.get(
    "/",
    response_model=CartOut,
    status_code=status.HTTP_200_OK,
    summary="Get cart",
    description="Returns the cart associated with the current user."
)
async def get_cart(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = await get_or_create_cart(db, current_user)
    await db.commit()
    await db.refresh(cart)
    return cart

@router.post(
    "/items",
    response_model=CartItemOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add item to cart",
    description="Adds an item to the cart associated with the current user."
)
async def add_cart_item(
    payload: CartItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = await get_or_create_cart(db, current_user)

    product = await db.get(Product, payload.product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    
    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.product_id == payload.product_id
        )
    )

    existing_item = result.scalar_one_or_none()

    requested_total_items = payload.quantity + (existing_item.quantity if existing_item else 0)

    if requested_total_items > product.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Requested quantity exceeds available stock."
        )

    if existing_item:
        existing_item.quantity = requested_total_items
        item = existing_item
    else:
        item = CartItem(
            cart_id=cart.id,
            product_id=payload.product_id,
            quantity=payload.quantity
        )
        db.add(item)

    await db.commit()
    await db.refresh(item)

    return CartItemOut(
        id=item.id,
        cart_id=item.cart_id,
        product_id=item.product_id,
        quantity=item.quantity,
        subtotal=item.quantity * product.price
    )