from app.core.resources.routers import generate_resource_router
from app.core.sys.variables import models, schemas
from fastapi import APIRouter

variables_router: APIRouter = APIRouter(include_in_schema=True)

sys_variables_router = generate_resource_router(
    **{
        "resource_name": "sys_variables",
        "url_prefix": "/sys/variables",
        "route_name_prefix": "sys:variables",
        "record": models.SysVariable,
        "list_schema": schemas.VariableListSchema,
        "record_schema": schemas.VariableSchema,
        "create_schema": schemas.VariableCreateSchema,
        "update_schema": schemas.VariableUpdateSchema,
    }
)

variables_router.include_router(sys_variables_router, tags=["sys_variables"])
