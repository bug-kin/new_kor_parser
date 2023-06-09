from datetime import datetime

from configs import config
from Database.schema import (CarBody, CarFuelType, CarGearbox, CarMark,
                             CarModel, Cars, CarSourceSite, CarTransmission,
                             ParserMonitoring)
from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


class Database:
    def __init__(self):
        self.engine = create_async_engine(
            config.db.engine,
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

    async def update_monitoring(self, status):
        session = self.session()
        stmt = (
            update(ParserMonitoring).
            where(ParserMonitoring.source == config.source)
        )
        try:
            if status:
                await session.execute(
                    stmt.values(status=status, parsed_at=datetime.now())
                )
            elif status is False:
                await session.execute(
                    stmt.values(
                        status=status,
                    )
                )
            else:
                await session.execute(
                    stmt.values(
                        status=status,
                        started_at=datetime.now()
                    )
                )

            await session.commit()

        except Exception as error:
            await session.rollback()
            print(f'{await self.time()} - [ ERROR ] {error}')

        finally:
            print(f'{await self.time()} - [ MONITORING ] Status updated')
            await session.close()
            return

    async def cars_processing(self, cars):
        if not cars:
            return

        await self.preloading()
        await self.update_for_delete_flag(
            cars[0].get('source'),
            cars[0].get('body_type')
        )

        for car in cars:
            await self.process_car(car)

        await self.engine.dispose()

    async def process_car(self, car):
        if car.get('deleted_at'):
            return

        session = self.session()
        source_id = self.car_sources.get(car.get("source"))
        res = await session.execute(
            select(Cars.id)
            .where(
                Cars.source_site_id == source_id,
                Cars.car_id == car.get('id')
            )
        )
        record_id = res.scalar_one_or_none()
        if record_id:
            try:
                await session.execute(
                    update(Cars)
                    .where(Cars.id == record_id)
                    .values(
                        grade_name=car.get('grade'),
                        year=car.get('year'),
                        price=car.get('price'),
                        mileage=car.get('mileage'),
                        engine_vol=car.get('engine'),
                        preview=car.get('preview'),
                        deleted_at=None
                    )
                )
                await session.commit()

            except Exception as error:
                await session.rollback()
                print(f'{await self.time()} - [ ERROR ] {error}')

            finally:
                await session.close()
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

        try:
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

        except Exception as error:
            await session.rollback()
            print(f'{await self.time()} - [ ERROR ] {error}')

        finally:
            await session.close()

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
        session = self.session()
        try:
            await session.execute(
                insert(table).values(val_dict).prefix_with('IGNORE')
            )
            await session.commit()

        except IntegrityError as error:
            print(f'{await self.time()} - [ ERROR ] {error}')

        except Exception as error:
            await session.rollback()
            print(f'{await self.time()} - [ ERROR ] {error}')

        finally:
            await session.close()

    async def update_for_delete_flag(self, source, body_type):
        source_id = self.car_sources.get(source)
        body_id = await self.get_or_create_record(
            target=body_type,
            dictionary=self.car_bodies,
            table=CarBody,
            field='kr_name',
        )
        session = self.session()
        try:
            await session.execute(
                update(Cars)
                .where(
                    Cars.source_site_id == source_id,
                    Cars.body_id == body_id
                )
                .values(deleted_at=datetime.now().date())
            )
            await session.commit()
            print(
                f'{await self.time()} - [ UPDATING ] The date is set for the deleted_at field for the body {body_type}.'
            )

        except Exception as error:
            await session.rollback()
            print(f'{await self.time()} - [ ERROR ] {error}')

        finally:
            await session.close()

    async def preloading(self):
        await self.get_all_records(table=CarSourceSite, dictionary=self.car_sources)
        await self.get_all_records(table=CarBody, dictionary=self.car_bodies)
        await self.get_all_records(table=CarMark, dictionary=self.car_marks)
        await self.get_all_records(table=CarModel, dictionary=self.car_models)
        await self.get_all_records(table=CarTransmission, dictionary=self.car_transmissions)
        await self.get_all_records(table=CarGearbox, dictionary=self.car_gearboxes)
        await self.get_all_records(table=CarFuelType, dictionary=self.car_fuel_types)

    async def get_all_records(self, table, dictionary):
        session = self.session()
        try:
            res = await session.execute(select(table))
            for rec in res.scalars():
                if hasattr(table, 'site'):
                    dictionary[rec.site] = rec.id

                if hasattr(table, 'name'):
                    dictionary[rec.name] = rec.id

                if hasattr(table, 'kr_name'):
                    dictionary[rec.kr_name] = rec.id

            await session.commit()

        except Exception as error:
            await session.rollback()
            print(f'{await self.time()} - [ ERROR ] {error}')

        finally:
            await session.close()

    @staticmethod
    async def time():
        return datetime.now().strftime("%d-%m-%Y %H:%M:%S")
