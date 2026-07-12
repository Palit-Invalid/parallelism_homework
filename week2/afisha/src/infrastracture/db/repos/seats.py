from src.infrastracture.db.repos.base import BaseRepository
from src.schemas.seats import SeatRead

class SeatsRepository(BaseRepository[SeatRead, None, None]):
    ...
