from fastapi import APIRouter

from src.api.dependencies import TicketsPurchasedSimulationServiceDep

router = APIRouter(prefix="/purchased-tickets")


@router.post("/simulate")
async def simulate(service: TicketsPurchasedSimulationServiceDep) -> None:
    await service.run_simulation()
