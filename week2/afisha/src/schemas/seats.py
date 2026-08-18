from pydantic import BaseModel


class SeatCreate(BaseModel):
    location_id: int
    sector: str
    row: int
    number: int
    x: int
    y: int


class SeatRead(SeatCreate):
    id: int


class SeatEdit(BaseModel):
    location_id: int | None = None
    sector: str | None = None
    row: int | None = None
    number: int | None = None
    x: int | None = None
    y: int | None = None
