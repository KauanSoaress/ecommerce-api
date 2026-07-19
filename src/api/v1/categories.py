from slugify import slugify
from sqlalchemy import select
from src.db.models.users import User
from sqlalchemy.exc import IntegrityError
from src.db.models.products import Product
from src.db.models.categories import Category
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.deps import get_db, get_current_user, get_current_admin_user
from src.schemas.category import CategoryCreate, CategoryUpdate, CategoryOut

router = APIRouter(prefix='/categories', tags=["categories"])

@router.get(
    "/",
    response_model=list[CategoryOut],
    status_code=status.HTTP_200_OK,
    summary="List categories",
    description="Returns all registered categories.",
)
async def get_categories(
    id: int | None = None,
    name: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = select(Category)

    if id:
        query = query.where(Category.id == id)
    
    if name:
        query = query.where(Category.name.ilike(f"%{name}%"))

    query = query.order_by(Category.name).offset(skip).limit(limit)

    result = await db.execute(query)
    categories = result.scalars().all()
    return categories

@router.post(
    "/",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create category",
    description="Create a new category"
)
async def create_category(
    payload: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    result = await db.execute(
        select(Category).where(Category.name == payload.name)
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A category with this name already exists."
        )

    category = Category(
        name=payload.name,
        slug=slugify(payload.name)
    )

    db.add(category)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A category with this name already exists.",
        )

    await db.refresh(category)

    return category

@router.get(
    "/{category_id}",
    response_model=CategoryOut,
    status_code=status.HTTP_200_OK,
    summary="Get category by ID",
    description="Returns a category by its ID."
)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    category = await db.get(Category, category_id)

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    return category

@router.patch(
    "/{category_id}",
    response_model=CategoryOut,
    status_code=status.HTTP_200_OK,
    summary="Update category",
    description="Update an existing category"
)
async def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    category = await db.get(Category, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )

    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data:
        result = await db.execute(
            select(Category).where(
                Category.name == update_data["name"],
                Category.id != category.id
            )
        )

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A category with this name already exists."
            )

        category.name = update_data["name"]
        category.slug = slugify(update_data["name"])

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A category with this name already exists.",
        )
    await db.refresh(category)

    return category

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete category",
    description="Delete an existing category"
)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    category = await db.get(Category, category_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found."
        )
    
    result = await db.execute(select(Product).where(Product.category_id == category_id).limit(1))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete category with associated products. Reassign or delete the products first.",
        )

    await db.delete(category)
    await db.commit()