from pydantic import BaseModel, ConfigDict

from src.schemas.seats import SeatRead


class LocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    city: str
    address: str


class LocationDetail(BaseModel):
    location: LocationRead
    seats: list[SeatRead]
