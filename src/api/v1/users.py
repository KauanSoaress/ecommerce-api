from sqlalchemy import select
from sqlite3 import IntegrityError
from src.db.models.users import User
from sqlalchemy.exc import IntegrityError
from src.core.security import hash_password
from sqlalchemy.ext.asyncio import AsyncSession
from src.schemas.user import UserCreate, UserOut, UserUpdate
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.deps import get_db, get_current_user, get_current_admin_user

router = APIRouter(prefix="/users", tags=["users"])

@router.post(
    "/",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Create a new user."
)
async def create_user(
    payload: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    result = await db.execute(
        select(User).where(User.name == payload.name)
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="A user with this name already exists."
        )
    
    result = await db.execute(
        select(User).where(User.email == payload.email)
    )

    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=409,
            detail="A user with this email already exists."
        )
    
    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        is_admin=payload.is_admin
    )

    db.add(user)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A user with this name or email already exists.",
        )
    
    await db.refresh(user)

    return user

@router.get(
    "/",
    response_model=list[UserOut],
    status_code=status.HTTP_200_OK,
    summary="List users",
    description="Returns all registered users.",
)
async def get_users(
    id: int | None = None,
    username: str | None = None,
    email: str | None = None,
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    query = select(User)

    if id:
        query = query.where(User.id == id)
    
    if username:
        query = query.where(User.username.ilike(f"%{username}%"))

    if email:
        query = query.where(User.email.ilike(f"%{email}%"))

    query = query.order_by(User.username).offset(skip).limit(limit)

    result = await db.execute(query)
    users = result.scalars().all()
    return users

@router.get("/me", response_model=UserOut)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user

@router.get(
    "/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Retrieve a user by their ID."
)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user

@router.patch(
    "/{user_id}",
    response_model=UserOut,
    status_code=status.HTTP_200_OK,
    summary="Update user by ID",
    description="Update a user's information by their ID."
)
async def update_user_by_id(
    user_id: int,
    payload: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    
    update_data = payload.model_dump(exclude_unset=True)

    if "name" in update_data:
        result = await db.execute(
            select(User).where(
                User.name == update_data["name"],
                User.id != user.id
            )
        )

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail="A user with this name already exists."
            )
    
    if "email" in update_data:
        result = await db.execute(
            select(User).where(
                User.email == update_data["email"],
                User.id != user.id
            )
        )

        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=409,
                detail="A user with this email already exists."
            )

    if "password" in update_data:
        update_data["hashed_password"] = hash_password(update_data.pop("password"))

    for field, value in update_data.items():
        setattr(user, field, value)
    
    try:
        await db.commit()
        await db.refresh(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already registered.",
        )

    return user

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user by ID",
    description="Delete a user by their ID."
)
async def delete_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    await db.delete(user)
    await db.commit()