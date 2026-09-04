from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_db, get_current_user
from src.services.cart import get_or_create_cart
from fastapi import APIRouter, Depends, HTTPException, status

from src.schemas.cart import CartOut
from src.schemas.cart_item import CartItemCreate, CartItemOut, CartItemUpdate

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
        cart.cart_items.append(item)
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


@router.patch(
    "/items/{item_id}",
    response_model=CartItemOut,
    status_code=status.HTTP_200_OK,
    summary="Update item",
    description="Update the quantity of a specific item in the cart"
)
async def update_cart_item(
    item_id: int,
    payload: CartItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = await get_or_create_cart(db, current_user)

    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.id == item_id
        )
    )

    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found."
        )

    update_data = payload.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    if not update_data:
        return item

    product = await db.get(Product, item.product_id)

    if "quantity" in update_data:
        if update_data["quantity"] > product.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested quantity exceeds available stock."
            )

    for key, value in update_data.items():
        setattr(item, key, value)

    await db.commit()
    await db.refresh(item)

    return item


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete item from cart",
    description="Deletes an item from the cart associated with the current user."
)
async def delete_cart_item(
    item_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    cart = await get_or_create_cart(db, current_user)

    result = await db.execute(
        select(CartItem).where(
            CartItem.cart_id == cart.id,
            CartItem.id == item_id
        )
    )

    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found."
        )

    await db.delete(item)
    await db.commit()
