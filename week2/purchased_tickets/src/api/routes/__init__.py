from fastapi import APIRouter

from src.api.routes.ws_purchased_tickets import purchased_tickets

__all__ = ("main_router",)


main_router = APIRouter()
main_router.include_router(purchased_tickets)
