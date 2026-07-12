from pydantic import BaseModel


class SeatCreate(BaseModel):
    location_id: int
    sector: str
    row: str
    number: int
    x: int
    y: int


class SeatRead(SeatCreate):
    id: int
