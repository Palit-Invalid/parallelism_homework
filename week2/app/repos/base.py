from pydantic import BaseModel
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base


class BaseRepository[ReadModelT: BaseModel, CreateModelT: BaseModel]:
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

    async def edit(self, data: ReadModelT, **filter_by) -> int:
        stmt = (
            update(self.model)
            .values(**data.model_dump(exclude_unset=True))
            .filter_by(**filter_by)
        )
        result = await self.session.execute(stmt)
        return result.rowcount

    async def delete(self, **filter_by) -> int:
        stmt = delete(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        return result.rowcount

    async def get_one(self, **filter_by) -> ReadModelT:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalar_one()
        return self.schema.model_validate(model, from_attributes=True)

    async def get_filtered(self, *filter, **filter_by) -> list[ReadModelT]:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        models = result.scalars().all()
        return [
            self.schema.model_validate(model, from_attributes=True)
            for model in result.scalars().all()
        ]
