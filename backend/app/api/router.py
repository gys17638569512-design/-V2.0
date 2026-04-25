from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.contacts import router as contacts_router
from app.api.routes.customers import router as customers_router
from app.api.routes.field_options import router as field_options_router
from app.api.routes.system import router as system_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(contacts_router)
api_router.include_router(customers_router)
api_router.include_router(field_options_router)
api_router.include_router(system_router)
