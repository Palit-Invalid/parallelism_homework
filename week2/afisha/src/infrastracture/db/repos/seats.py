from src.infrastracture.db.repos.base import BaseRepository
from src.schemas.seats import SeatRead, SeatCreate
from src.infrastracture.db.models import Seat


class SeatsRepository(BaseRepository[SeatRead, SeatCreate, None]):
    model = Seat
    schema = SeatRead
