from fastapi import APIRouter
from app.modules.prompts.routing import get_router__prompts


api_router: APIRouter = APIRouter(include_in_schema=True)

api_router.include_router(get_router__prompts(), include_in_schema=True)
