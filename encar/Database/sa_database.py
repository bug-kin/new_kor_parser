from asyncio import create_task, gather
from datetime import datetime

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from configs import config
from Database.schema import (
    CarBody,
    CarFuelType,
    CarGearbox,
    CarMark,
    CarModel,
    Cars,
    CarSourceSite,
    CarTransmission,
)


class Database:
    def __init__(self):
        self.engine = create_async_engine(config.connection.engine, echo=True)
        self.session = async_sessionmaker(bind=self.engine)
        self.car_sources = None
        self.car_bodies = None
        self.car_marks = None
        self.car_models = None
        self.car_transmissions = None
        self.car_gearboxes = None
        self.car_fuel_types = None

    async def cars_processing(self, cars):
        await self.preloading()
        batch = []
        for car in cars:
            await self.process_car(car)
            # if len(batch) == 10:
            #     gather(*batch)
            #     batch.clear()

            # batch.append(create_task(self.process_car(car)))

    async def process_car(self, car):
        async with self.session() as session:
            if car.get("deleted_at"):
                stmt = (
                    update(Cars)
                    .where(
                        Cars.source_site_id == self.car_sources[car["source"]],
                        Cars.car_id == car.get("id"),
                    )
                    .values(deleted_at=datetime.now().date())
                )
                await session.execute(stmt)
                await session.commit()
                return

            source_id = self.car_sources.get(car.get("source"))
            if not (body_id := self.car_bodies.get(car.get("body_type"))):
                stmt = insert(CarBody).values(kr_name=car.get("body_type"))
                await session.execute(stmt)
                await session.commit()
                await self.get_car_bodies()
                body_id = self.car_bodies.get(car.get("body_type"))

    async def preloading(self):
        await self.get_colors()
        await self.get_car_bodies()
        await self.get_car_marks()
        await self.get_car_models()
        await self.get_car_transmissions()
        await self.get_car_gearboxes()
        await self.get_car_fuel_types()

    async def get_car_fuel_types(self):
        async with self.session() as session:
            stmt = select(CarFuelType)
            result = await session.execute(stmt)
            self.car_fuel_types = {
                record.kr_name: record.id for record in result.scalars()
            }

    async def get_car_gearboxes(self):
        async with self.session() as session:
            stmt = select(CarGearbox)
            result = await session.execute(stmt)
            self.car_gearboxes = {
                record.kr_name: record.id for record in result.scalars()
            }

    async def get_car_transmissions(self):
        async with self.session() as session:
            stmt = select(CarTransmission)
            result = await session.execute(stmt)
            self.car_transmissions = {
                record.name: record.id for record in result.scalars()
            }

    async def get_car_models(self):
        async with self.session() as session:
            stmt = select(CarModel)
            result = await session.execute(stmt)
            self.car_models = {record.kr_name: record.id for record in result.scalars()}

    async def get_car_marks(self):
        async with self.session() as session:
            stmt = select(CarMark)
            result = await session.execute(stmt)
            self.car_marks = {record.kr_name: record.id for record in result.scalars()}

    async def get_car_bodies(self):
        async with self.session() as session:
            stmt = select(CarBody)
            result = await session.execute(stmt)
            self.car_bodies = {record.kr_name: record.id for record in result.scalars()}

    async def get_colors(self):
        async with self.session() as session:
            stmt = select(CarSourceSite)
            result = await session.execute(stmt)
            self.car_sources = {record.site: record.id for record in result.scalars()}
