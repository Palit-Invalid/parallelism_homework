from src.infrastracture.db.repos.base import BaseRepository
from src.schemas.seats import SeatRead, SeatCreate, SeatEdit
from src.infrastracture.db.models import Seat


class SeatsRepository(BaseRepository[SeatRead, SeatCreate, SeatEdit]):
    model = Seat
    schema = SeatRead
