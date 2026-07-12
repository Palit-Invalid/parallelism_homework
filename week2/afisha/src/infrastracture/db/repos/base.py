from asyncpg import LockNotAvailableError
from sqlalchemy.exc import DBAPIError
from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from src.domain.exceptions import ObjectLockedError
from src.infrastracture.db.models.base import Base
from src.log import logger

class BaseRepository[
    ReadModelT: BaseModel,
    CreateModelT: BaseModel,
    EditModelT: BaseModel,
]:
    model: type[Base]
    schema: type[BaseModel]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_one(self, data: CreateModelT) -> ReadModelT:
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(stmt)
        model = result.scalar_one()
        return self.schema.model_validate(model, from_attributes=True)

    async def add_bulk(self, data: list[CreateModelT]):
        stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(stmt)

    async def edit(self, data: EditModelT, *filter) -> int:
        stmt = (
            update(self.model)
            .values(**data.model_dump(exclude_unset=True))
            .filter(*filter)
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def delete(self, *filter) -> int:
        stmt = delete(self.model).filter(*filter)
        result = await self.session.execute(stmt)
        return result.rowcount

    async def get_one(self, for_update: bool = False, *filter) -> ReadModelT:
        query = select(self.model).filter(*filter)
        if for_update:
            query.with_for_update()
        result = await self.session.execute(query)
        model = result.scalar_one()
        return self.schema.model_validate(model, from_attributes=True)

    async def get_filtered(self, *filter, lock: bool = False) -> list[ReadModelT]:
        query = select(self.model).filter(*filter)
        if lock:
            query = query.with_for_update(nowait=True)

        try:
            result = await self.session.execute(query)
        except DBAPIError as exc:
            if not exc.orig:
                raise exc
            if isinstance(exc.orig.__cause__, LockNotAvailableError):
                logger.debug('Unable to get data from database because its locked')
                raise ObjectLockedError

        models = result.scalars().all()
        return [
            self.schema.model_validate(model, from_attributes=True) for model in models
        ]
