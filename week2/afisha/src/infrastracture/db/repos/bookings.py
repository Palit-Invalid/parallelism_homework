from src.infrastracture.db.repos.base import BaseRepository
from src.infrastracture.db.models import Booking
from src.schemas.bookings import BookingReadDB, BookingCreateDB, BookingEditDB


class BookingsRepository(BaseRepository[BookingReadDB, BookingCreateDB, BookingEditDB]):
    model = Booking
    schema = BookingReadDB
