from pydantic import BaseModel, Field


class BookingCreate(BaseModel):
    seat_ids: list[int] = Field(min_length=1)
