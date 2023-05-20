from app.core.sys.users.routing import users_router
from app.core.sys.variables.routing import variables_router
from app.modules.vendors.routing import vendors_router
from fastapi import APIRouter



api_router: APIRouter = APIRouter(include_in_schema=True)

api_router.include_router(users_router)
api_router.include_router(variables_router)
api_router.include_router(vendors_router)
