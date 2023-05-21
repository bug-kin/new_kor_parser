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
        self.engine = create_async_engine(
            config.connection.engine,
            pool_recycle=180,
            echo=True,
        )
        self.session = async_sessionmaker(bind=self.engine)
        self.car_sources = dict()
        self.car_bodies = dict()
        self.car_marks = dict()
        self.car_models = dict()
        self.car_transmissions = dict()
        self.car_gearboxes = dict()
        self.car_fuel_types = dict()

    async def cars_processing(self, cars):
        if not cars:
            return

        await self.preloading()
        await self.update_for_delete_flag(cars[0].get('source'), cars[0].get('body_type'))

        batch = []
        for car in cars:
            if len(batch) == 10:
                await gather(*batch)
                batch.clear()
            
            batch.append(create_task(self.process_car(car)))
        
        await gather(*batch)
        batch.clear()

    async def process_car(self, car):
        async with self.session() as session:
            source_id = self.car_sources.get(car.get("source"))
            res = await session.execute(
                select(Cars.id)
                .where(
                    Cars.source_site_id==source_id,
                    Cars.car_id==car.get('id')
                )
            )
            record_id = res.scalar_one_or_none()
            if record_id:
                await session.execute(
                    update(Cars)
                    .where(Cars.id==record_id)
                    .values(deleted_at=None)
                )
                await session.commit()
                return

            body_id = await self.get_or_create_record(
                target=car.get('body_type'),
                dictionary=self.car_bodies,
                table=CarBody,
                field='kr_name',
            )
            mark_id = await self.get_or_create_record(
                target=car.get('mark'),
                dictionary=self.car_marks,
                table=CarMark,
                field='kr_name',
            ),
            model_id = await self.get_or_create_record(
                target=car.get('model'),
                dictionary=self.car_models,
                table=CarModel,
                field='kr_name',
            )
            transmission_id = await self.get_or_create_record(
                target=car.get('transmission'),
                dictionary=self.car_transmissions,
                table=CarTransmission,
                field='name',
            )
            gearbox_id = await self.get_or_create_record(
                target=car.get('gearbox'),
                dictionary=self.car_gearboxes,
                table=CarGearbox,
                field='kr_name'
            )
            fuel_type_id = await self.get_or_create_record(
                target=car.get('fuel'),
                dictionary=self.car_fuel_types,
                table=CarFuelType,
                field='kr_name'
            )

            await session.execute(
                insert(Cars)
                .values(
                    source_site_id=source_id,
                    car_id=car.get('id'),
                    body_id=body_id,
                    mark_id=mark_id,
                    model_id=model_id,
                    grade_name=car.get('grade'),
                    year=car.get('year'),
                    price=car.get('price'),
                    mileage=car.get('mileage'),
                    gearbox_id=gearbox_id,
                    transmission_id=transmission_id,
                    fuel_type_id=fuel_type_id,
                    engine_vol=car.get('engine'),
                    preview=car.get('preview')
                )
            )
            await session.commit()

    async def get_or_create_record(self, target, dictionary, table, field):
        if not target:
            return None

        while True:
            target_id = dictionary.get(target)
            if target_id:
                return target_id

            await self.creating_record(table=table, val_dict={f'{field}': target})
            await self.get_all_records(table=table, dictionary=dictionary)

    async def creating_record(self, table, val_dict):
        async with self.session() as session:
            await session.execute(insert(table).values(val_dict))
            await session.commit()

    async def update_for_delete_flag(self, source, body_type):
        source_id = self.car_sources.get(source)
        body_id = await self.get_or_create_record(
            target=body_type,
            dictionary=self.car_bodies,
            table=CarBody,
            field='kr_name',
        )
        async with self.session() as session:
            await session.execute(
                update(Cars)
                .where(
                    Cars.source_site_id==source_id,
                    Cars.body_id==body_id
                )
                .values(deleted_at=datetime.now().date())
            )
            await session.commit()
        
        print(
            f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ UPDATING ] The date is set for the deleted_at field for the body {body_type}.'
        )

    async def preloading(self):
        tasks = [
            create_task(self.get_all_records(table=CarSourceSite, dictionary=self.car_sources)),
            create_task(self.get_all_records(table=CarBody, dictionary=self.car_bodies)),
            create_task(self.get_all_records(table=CarMark, dictionary=self.car_marks)),
            create_task(self.get_all_records(table=CarModel, dictionary=self.car_models)),
            create_task(self.get_all_records(table=CarTransmission, dictionary=self.car_transmissions)),
            create_task(self.get_all_records(table=CarGearbox, dictionary=self.car_gearboxes)),
            create_task(self.get_all_records(table=CarFuelType, dictionary=self.car_fuel_types))
        ]
        await gather(*tasks)

    async def get_all_records(self, table, dictionary):
        async with self.session() as session:     
            res = await session.execute(select(table))
            for rec in res.scalars():
                if hasattr(table, 'site'):
                    dictionary[rec.site] = rec.id
                
                if hasattr(table, 'name'):
                    dictionary[rec.name] = rec.id
                
                if hasattr(table, 'kr_name'):
                    dictionary[rec.kr_name] = rec.id
