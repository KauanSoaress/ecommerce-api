from fastapi import APIRouter

from src.api.v1 import  users

api_router = APIRouter()

# api_router.include_router(auth.router)
api_router.include_router(users.router)
# api_router.include_router(products.router)
# api_router.include_router(categories.router)
# api_router.include_router(carts.router)
# api_router.include_router(orders.router)
# api_router.include_router(coupons.router)