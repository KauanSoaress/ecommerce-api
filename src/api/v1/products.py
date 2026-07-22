from sqlalchemy import select
from src.db.models.users import User
from sqlalchemy.exc import IntegrityError
from src.db.models.products import Product
from src.db.models.categories import Category
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.storage import upload_image, update_image, delete_image
from src.api.deps import get_db, get_current_user, get_current_admin_user
from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile
from src.schemas.product import ProductCreate, ProductOut, ProductUpdate, ProductStockUpdate

router = APIRouter(prefix='/products', tags=["products"])

@router.get(
    "/",
    response_model=list[ProductOut],
    status_code=status.HTTP_200_OK,
    summary="List products",
    description="Returns all registered products.",
)
async def get_products(
    id: int | None = None,
    category_id: int | None = None,
    name: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Product)

    if id:
        query = query.where(Product.id == id)

    if category_id:
        query = query.where(Product.category_id == category_id)

    if name:
        query = query.where(Product.name.ilike(f"%{name}%"))

    query = query.order_by(Product.name).offset(skip).limit(limit)

    result = await db.execute(query)
    products = result.scalars().all()
    return products

@router.post(
    "/",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create product",
    description="Create a new product"
)
async def create_product(
    payload: ProductCreate = Depends(ProductCreate.as_form),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    result = await db.execute(
        select(Category).where(Category.id == payload.category_id)
    )

    category = result.scalar_one_or_none()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )
    
    result = await db.execute(
        select(Product).where(Product.name == payload.name)
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="A product with this name already exists."
        )

    url, public_id = await upload_image(file)

    product = Product(
        name=payload.name,
        description=payload.description,
        price=payload.price,
        stock=payload.stock,
        category_id=payload.category_id,
        image_url=url,
        image_public_id=public_id
    )

    db.add(product)

    try:
        await db.commit()
        await db.refresh(product)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Database integrity error.",
        )
    
    return product

@router.patch(
    "/{product_id}",
    response_model=ProductOut,
    status_code=status.HTTP_200_OK,
    summary="Update product",
    description="Update an existing product"
)
async def update_product(
    product_id: int,
    payload: ProductUpdate = Depends(ProductUpdate.as_form),
    file: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    product = await db.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    
    update_data = payload.model_dump(
        exclude_unset=True,
        exclude_none=True
    )

    if not update_data and not file:
        return product

    if "name" in update_data:
        result = await db.execute(
            select(Product).where(
                Product.name == update_data["name"],
                Product.id != product.id
            )
        )

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail="A product with this name already exists."
            )

    if "category_id" in update_data:
        result = await db.execute(
            select(Category).where(Category.id == update_data["category_id"])
        )

        if result.scalar_one_or_none() is None:
            raise HTTPException(
                status_code=404,
                detail="Category not found."
            )

    for field, value in update_data.items():
        setattr(product, field, value)

    if file:
        url, public_id = await update_image(file, product.image_public_id)
        product.image_url = url
        product.image_public_id = public_id

    try:
        await db.commit()
        await db.refresh(product)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A product with this name already exists.",
        )

    return product

@router.patch(
    "/{product_id}/stock",
    response_model=ProductOut,
    status_code=status.HTTP_200_OK,
    summary="Update product stock",
    description="Update the stock of an existing product"
)
async def update_product_stock(
    product_id: int,
    payload: ProductStockUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    product = await db.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )

    product.stock = payload.stock
    await db.commit()
    await db.refresh(product)

    return product

@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product",
    description="Delete a product by its ID"
)
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    product = await db.get(Product, product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found."
        )
    
    if product.image_public_id:
        await delete_image(product.image_public_id)

    await db.delete(product)
    await db.commit()