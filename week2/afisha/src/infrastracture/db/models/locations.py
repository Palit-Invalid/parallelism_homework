from sqlalchemy.orm import Mapped, mapped_column

from src.infrastracture.db.models.base import Base


class Location(Base):
    """Площадка, где проходят мероприятия (например, Лужники, ВТБ-Арена)."""

    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    city: Mapped[str]
    address: Mapped[str]
