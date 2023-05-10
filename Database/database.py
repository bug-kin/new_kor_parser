from datetime import datetime

import pymysql
from pymysql.err import OperationalError
from .database_configs import data


class Database:
    def __init__(
        self,
    ):
        self.connection = self.connecting()
        self.sources = self.get_all_records(
            data.schema.source.table, data.schema.source.fields
        )
        self.car_bodies = self.get_all_records(
            data.schema.car_body.table, data.schema.car_body.fields
        )
        self.car_marks = self.get_all_records(
            data.schema.car_mark.table, data.schema.car_mark.fields
        )
        self.models = self.get_all_records(
            data.schema.car_model.table, data.schema.car_model.fields
        )
        self.transmissions = self.get_all_records(
            data.schema.transmission.table, data.schema.transmission.fileds
        )
        self.gearboxes = self.get_all_records(
            data.schema.gearbox.table, data.schema.gearbox.fields
        )
        self.fuel_types = self.get_all_records(
            data.schema.fuel_type.table, data.schema.fuel_type.fields
        )

    @staticmethod
    def connecting():
        return pymysql.Connection(
            host=data.connection.host,
            user=data.connection.user,
            password=data.connection.password,
            db=data.connection.database,
            cursorclass=pymysql.cursors.DictCursor,
        )

    def insert_or_update_car(self, cars):
        batch = []
        for car in cars:
            source_site_id = self.sources[car["source"]]
            if car.get("deleted_at"):
                continue

            if self.check_car_existance(source_site_id, car.get("id")):
                self.update_timestamp(source_site_id, car.get("id"))
                continue

            if not (body_type_id := self.car_bodies.get(car.get("body_type"))):
                self.insert_new_record(
                    table=data.schema.car_body.table,
                    field=data.schema.car_body.fields[1],
                    data=car.get("body_type"),
                )
                self.car_bodies = self.get_all_records(
                    data.schema.car_body.table, data.schema.car_body.fields
                )
                body_type_id = self.car_bodies.get(car.get("body_type"))

            if not (mark_id := self.car_marks.get(car.get("mark"))):
                self.insert_new_record(
                    table=data.schema.car_mark.table,
                    field=data.schema.car_mark.fields[1],
                    data=car.get("mark"),
                )
                self.car_marks = self.get_all_records(
                    data.schema.car_mark.table, data.schema.car_mark.fields
                )
                mark_id = self.car_marks.get(car.get("mark"))

            if not (model_id := self.models.get(car.get("model"))):
                self.insert_new_record(
                    table=data.schema.car_model.table,
                    field=data.schema.car_model.fields[1],
                    data=car.get("model"),
                )
                self.models = self.get_all_records(
                    data.schema.car_model.table, data.schema.car_model.fields
                )
                model_id = self.models.get(car.get("model"))

            if car.get("transmission"):
                if not (
                    transmission_id := self.transmissions.get(car.get("transmission"))
                ):
                    self.insert_new_record(
                        table=data.schema.transmission.table,
                        field=data.schema.transmission.fileds[1],
                        data=car.get("transmission"),
                    )
                    self.transmissions = self.get_all_records(
                        data.schema.transmission.table, data.schema.transmission.fileds
                    )
                    transmission_id = self.transmissions.get(car.get("transmission"))
            else:
                transmission_id = None

            if car.get("gearbox"):
                if not (gearbox_id := self.gearboxes.get(car.get("gearbox"))):
                    self.insert_new_record(
                        table=data.schema.gearbox.table,
                        field=data.schema.gearbox.fields[1],
                        data=car.get("gearbox"),
                    )
                    self.gearboxes = self.get_all_records(
                        data.schema.gearbox.table, data.schema.gearbox.fields
                    )
                    gearbox_id = self.gearboxes.get(car["gearbox"])
            else:
                gearbox_id = None

            if car.get("fuel"):
                if not (fuel_type_id := self.fuel_types.get(car.get("fuel"))):
                    # self.insert_new_record('fuel_type', 'kr_name', car.get('fuel'))
                    self.insert_new_record(
                        table=data.schema.fuel_type,
                        field=data.schema.fuel_type.fields[1],
                        data=car.get("fuel"),
                    )
                    self.fuel_types = self.get_all_records(
                        data.schema.fuel_type.table, data.schema.fuel_type.fields
                    )
                    fuel_type_id = self.fuel_types.get(car.get("fuel"))
            else:
                fuel_type_id = None

            if len(batch) == 500:
                self.inserting_cars(batch)
                batch.clear()

            batch.append(
                (
                    source_site_id,
                    car["id"],
                    body_type_id,
                    mark_id,
                    model_id,
                    car["grade"],
                    gearbox_id,
                    transmission_id,
                    fuel_type_id,
                    car["price"],
                    car["year"],
                    car["mileage"],
                    car["engine"],
                    car["preview"],
                )
            )

        if batch:
            self.inserting_cars(batch)

    def get_all_records(self, table, fields):
        try:
            query = f'SELECT {", ".join(fields)} FROM {table};'
            print(
                f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ SELECT ] {query}'
            )
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                return {
                    row.get(fields[1]): row.get(fields[0]) for row in cursor.fetchall()
                }

        except (TimeoutError, OperationalError):
            print(
                f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
            )
            self.connection.close()
            self.connection = self.connecting()

    def insert_new_record(self, table, field, data):
        try:
            query = f"INSERT INTO {table} ({field}) VALUES ('{data}');"
            print(
                f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ INSERT ] {query}'
            )
            with self.connection.cursor() as cursor:
                cursor.execute(query)

            self.connection.commit()

        except (TimeoutError, OperationalError):
            print(
                f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
            )
            self.connection.close()
            self.connection = self.connecting()

        except Exception as error:
            self.connection.rollback()
            print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}')

    def inserting_cars(self, data):
        print(
            f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ INSERTING ] - Inserting cars...'
        )
        attempt = 1
        query = "INSERT INTO cars (source_site_id, car_id, body_id, mark_id, model_id, grade_name, gearbox_id, transmission_id, fuel_type_id, price, year, mileage, engine_vol, preview) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        while True:
            try:
                with self.connection.cursor() as cursor:
                    cursor.executemany(query, data)

                self.connection.commit()
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ INSERTED ] - Inserted [{len(data)}]'
                )
                return

            except (TimeoutError, OperationalError):
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
                )
                self.connection.close()
                self.connection = self.connecting()

            except Exception as error:
                self.connection.rollback()
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}'
                )

            if attempt == 3:
                return

            attempt += 1

    def check_car_existance(self, source_site_id, car_id):
        attempts = 2
        while True:
            print(
                f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ CHECK ] Checking the car {car_id} for existence'
            )
            try:
                with self.connection.cursor() as cursor:
                    result = cursor.execute(
                        f"SELECT id, car_id FROM cars WHERE source_site_id={source_site_id} and car_id={car_id};"
                    )
                    if result:
                        print(
                            f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ CHECK ] Car {car_id} exist'
                        )
                        return True

                    print(
                        f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ CHECK ] Car {car_id} doesn\'t exist'
                    )
                    return False

            except (TimeoutError, OperationalError) as error:
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}'
                )
                self.connection.close()
                self.connection = self.connecting()

            if attempts == 0:
                return

            attempts -= 1

    def update_timestamp(self, source_site_id, car_id):
        attempts = 2
        while True:
            try:
                with self.connection.cursor() as cursor:
                    print(
                        f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ UPDATE ] Car {car_id} updating relevance'
                    )
                    cursor.execute(
                        f"UPDATE cars SET updated_at=now() WHERE source_site_id={source_site_id} and car_id={car_id};"
                    )

                self.connection.commit()

            except (TimeoutError, OperationalError) as error:
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}'
                )
                self.connection.close()
                self.connection = self.connecting()

            except Exception as error:
                self.connection.rollback()
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}'
                )

            if attempts == 0:
                return

            attempts -= 1


class Deprecated:
    class Getting:
        def get_sources(self):
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT id, site FROM source;")
                    return {row.get("site"): row.get("id") for row in cursor.fetchall()}

            except (TimeoutError, OperationalError):
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
                )
                self.connection.close()
                self.connection = self.connecting()

        def get_car_bodies(self):
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT id, kr_name FROM car_body;")
                    return {
                        row.get("kr_name"): row.get("id") for row in cursor.fetchall()
                    }

            except (TimeoutError, OperationalError):
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
                )
                self.connection.close()
                self.connection = self.connecting()

        def get_car_marks(self):
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT id, kr_name FROM car_mark;")
                    return {
                        row.get("kr_name"): row.get("id") for row in cursor.fetchall()
                    }

            except (TimeoutError, OperationalError):
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
                )
                self.connection.close()
                self.connection = self.connecting()

        def get_models(self):
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT id, kr_name FROM model;")
                    return {
                        row.get("kr_name"): row.get("id") for row in cursor.fetchall()
                    }

            except (TimeoutError, OperationalError):
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
                )
                self.connection.close()
                self.connection = self.connecting()

        def get_transmissions(self):
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT id, name FROM drive_type;")
                    return {row.get("name"): row.get("id") for row in cursor.fetchall()}

            except (TimeoutError, OperationalError):
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
                )
                self.connection.close()
                self.connection = self.connecting()

        def get_gearboxes(self):
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT id, kr_name FROM gearbox;")
                    return {
                        row.get("kr_name"): row.get("id") for row in cursor.fetchall()
                    }

            except (TimeoutError, OperationalError):
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
                )
                self.connection.close()
                self.connection = self.connecting()

        def get_fuel_types(self):
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT id, kr_name FROM fuel_type;")
                    return {
                        row.get("kr_name"): row.get("id") for row in cursor.fetchall()
                    }

            except (TimeoutError, OperationalError):
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
                )
                self.connection.close()
                self.connection = self.connecting()

    class Inserting:
        def insert_new_fuel_type(self, fuel_type):
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(
                        f"INSERT INTO fuel_type (kr_name) VALUES ('{fuel_type}');"
                    )

                self.connection.commit()

            except (TimeoutError, OperationalError):
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
                )
                self.connection.close()
                self.connection = self.connecting()

            except Exception as error:
                self.connection.rollback()
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}'
                )

        def insert_new_body_type(self, body_type):
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(
                        f"INSERT INTO car_body (kr_name) VALUES ('{body_type}');"
                    )

                self.connection.commit()

            except (TimeoutError, OperationalError):
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
                )
                self.connection.close()
                self.connection = self.connecting()

            except Exception as error:
                self.connection.rollback()
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}'
                )

        def insert_new_model(self, model):
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(f"INSERT INTO model (kr_name) VALUES ('{model}');")

                self.connection.commit()

            except (TimeoutError, OperationalError):
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
                )
                self.connection.close()
                self.connection = self.connecting()

            except Exception as error:
                self.connection.rollback()
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}'
                )

        def insert_new_gearbox(self, gearbox):
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(
                        f"INSERT INTO gearbox (kr_name) VALUES ('{gearbox}');"
                    )

                self.connection.commit()

            except (TimeoutError, OperationalError):
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
                )
                self.connection.close()
                self.connection = self.connecting()

            except Exception as error:
                self.connection.rollback()
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}'
                )

        def insert_new_transmission(self, transmission):
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(
                        f"INSERT INTO drive_type (name) VALUES ('{transmission}');"
                    )

                self.connection.commit()

            except (TimeoutError, OperationalError):
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
                )
                self.connection.close()
                self.connection = self.connecting()

            except Exception as error:
                self.connection.rollback()
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}'
                )

        def insert_new_car_mark(self, mark):
            try:
                with self.connection.cursor() as cursor:
                    cursor.execute(f"INSERT INTO car_mark (kr_name) VALUES ('{mark}');")

                self.connection.commit()

            except (TimeoutError, OperationalError):
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TimeOut ] TimeoutError'
                )
                self.connection.close()
                self.connection = self.connecting()

            except Exception as error:
                self.connection.rollback()
                print(
                    f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}'
                )
