from fastapi import APIRouter

from app.api.routes.auth import router as auth_router
from app.api.routes.certificates import router as certificates_router
from app.api.routes.contacts import router as contacts_router
from app.api.routes.customers import router as customers_router
from app.api.routes.equipment import router as equipment_router
from app.api.routes.field_options import router as field_options_router
from app.api.routes.sites import router as sites_router
from app.api.routes.system import router as system_router

api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(certificates_router)
api_router.include_router(contacts_router)
api_router.include_router(customers_router)
api_router.include_router(equipment_router)
api_router.include_router(field_options_router)
api_router.include_router(sites_router)
api_router.include_router(system_router)
