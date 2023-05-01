import pymysql
from datetime import datetime


class Database:
    def __init__(self,):
        self.connection_dict = {
            'host': 'pepe.foundation',
            'user': 'homestead',
            'password': 'homestead',
            'db': 'homestead',
            'cursorclass': pymysql.cursors.DictCursor
        }
        self.sources = self.get_sources()
        self.car_bodies = self.get_car_bodies()
        self.car_marks = self.get_car_marks()
        self.models = self.get_models()
        self.transmissions = self.get_transmissions()
        self.gearboxes = self.get_gearboxes()
        self.fuel_types = self.get_fuel_types()
    
    
    def insert_or_update_car(self, cars):
        data = []
        for car in cars:
            site_id = self.sources['bobaedream']
            if self.check_car_existance(site_id, car['id']):
                self.update_updated_at(site_id, car['id'])
                continue

            if not (body_type_id := self.car_bodies.get(car['body_type'])):
                self.insert_new_body_type(car['body_type'])
                self.car_bodies = self.get_car_bodies()
                body_type_id = self.car_bodies[car['body_type']]
            
            if not (mark_id := self.car_marks.get(car['mark'])):
                self.insert_new_car_mark(car['mark'])
                self.car_marks = self.get_car_marks()
                mark_id = self.car_marks[car['mark']]
            
            if not (model_id := self.models.get(car['model'])):
                self.insert_new_model(car['model'])
                self.models = self.get_models()
                model_id = self.models[car['model']]
            
            if car['transmission'] and not (transmission_id := self.transmissions.get(car['transmission'])):
                self.insert_new_transmission(car['transmission'])
                self.transmissions = self.get_transmissions()
                transmission_id = self.transmissions[car['transmission']]
            
            if not (gearbox_id := self.gearboxes.get(car['gearbox'])):
                self.insert_new_gearbox(car['gearbox'])
                self.gearboxes = self.get_gearboxes()
                gearbox_id = self.gearboxes[car['gearbox']]
            
            if not (fuel_type_id := self.fuel_types.get(car['fuel'])):
                self.insert_new_fuel_type(car['fuel'])
                self.fuel_types = self.get_fuel_types()
                fuel_type_id = self.fuel_types[car['fuel']]
            
            if len(data) == 100:
                self.inserting_cars(data)
                data.clear()

            data.append(
                (site_id, car['id'], body_type_id, mark_id, model_id, car['grade'], gearbox_id, transmission_id, fuel_type_id, car['price'], car['year'], car['mileage'], car['engine'], car['preview'])
            )

        self.inserting_cars(data)

    
    def inserting_cars(self, data):
        attempt = 1
        query = 'INSERT INTO car (site_id, car_id, car_body_id, mark_id, model_id, grade_name, gearbox_id, drive_type_id, fuel_type_id, price, year, mileage, engine_vol, preview) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
        while True:
            try:
                with pymysql.connect(**self.connection_dict) as conn:
                    try:
                        with conn.cursor() as cursor:
                            cursor.executemany(query, data)
                    
                        conn.commit()
                        return
                    except Exception as error:
                        conn.rollback()
                        print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}')

            except Exception as error:
                print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}')
                if attempt == 3:
                    return

                attept += 1
    
    def check_car_existance(self, site_id, car_id):
        print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ CHECK ] - Checking the car {car_id} for existence')
        with pymysql.connect(**self.connection_dict) as conn:
            with conn.cursor() as cursor:
                result = cursor.execute(f'SELECT id, car_id FROM car WHERE site_id={site_id} and car_id={car_id};')
                if result:
                    print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ CHECK ] - Car {car_id} exist')
                    return True
                
                print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ CHECK ] - Car {car_id} doesn\'t exist')
                return False

    def update_updated_at(self, site_id, car_id):
        with pymysql.connect(**self.connection_dict) as conn:
            try:
                with conn.cursor() as cursor:
                    print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ UPDATE ] - Car {car_id} updating relevance')
                    cursor.execute(f'UPDATE car SET updated_at=now() WHERE site_id={site_id} and car_id={car_id};')

                conn.commit()
            except Exception as error:
                conn.rollback()
                print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}')

    def get_sources(self):
        with pymysql.connect(**self.connection_dict) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id, site FROM source;')
                return {
                    row.get('site'): row.get('id')
                    for row in cursor.fetchall()
                }
    
    def get_car_bodies(self):
        with pymysql.connect(**self.connection_dict) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id, kr_name FROM car_body;')
                return {
                    row.get('kr_name'): row.get('id')
                    for row in cursor.fetchall()
                }
    
    def insert_new_body_type(self, body_type):
        with pymysql.connect(**self.connection_dict) as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(f'INSERT INTO car_body (kr_name) VALUES (\'{body_type}\');')
                
                conn.commit()
            except Exception as error:
                conn.rollback()
                print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}')
            
    def get_car_marks(self):
        with pymysql.connect(**self.connection_dict) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id, kr_name FROM car_mark;')
                return {
                    row.get('kr_name'): row.get('id')
                    for row in cursor.fetchall()
                }
    
    def insert_new_car_mark(self, mark):
        with pymysql.connect(**self.connection_dict) as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(f'INSERT INTO car_mark (kr_name) VALUES (\'{mark}\');')
                
                conn.commit()
            except Exception as error:
                conn.rollback()
                print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}')
    
    def get_models(self):
        with pymysql.connect(**self.connection_dict) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id, kr_name FROM model;')
                return {
                    row.get('kr_name'): row.get('id')
                    for row in cursor.fetchall()
                }
    
    def insert_new_model(self, model):
        with pymysql.connect(**self.connection_dict) as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(f'INSERT INTO model (kr_name) VALUES (\'{model}\');')
                
                conn.commit()
            except Exception as error:
                conn.rollback()
                print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}')
    
    def get_transmissions(self):
        with pymysql.connect(**self.connection_dict) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id, name FROM drive_type;')
                return {
                    row.get('name'): row.get('id')
                    for row in cursor.fetchall()
                }
    
    def insert_new_transmission(self, transmission):
        with pymysql.connect(**self.connection_dict) as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(f'INSERT INTO drive_type (name) VALUES (\'{transmission}\');')
                
                conn.commit()
            except Exception as error:
                conn.rollback()
                print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}')
    
    def get_gearboxes(self):
        with pymysql.connect(**self.connection_dict) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id, kr_name FROM gearbox;')
                return {
                    row.get('kr_name'): row.get('id')
                    for row in cursor.fetchall()
                }

    def insert_new_gearbox(self, gearbox):
        with pymysql.connect(**self.connection_dict) as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(f'INSERT INTO gearbox (kr_name) VALUES (\'{gearbox}\');')
                
                conn.commit()
            except Exception as error:
                conn.rollback()
                print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}')
    
    def get_fuel_types(self):
        with pymysql.connect(**self.connection_dict) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT id, kr_name FROM fuel_type;')
                return {
                    row.get('kr_name'): row.get('id')
                    for row in cursor.fetchall()
                }

    def insert_new_fuel_type(self, fuel_type):
        with pymysql.connect(**self.connection_dict) as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(f'INSERT INTO fuel_type (kr_name) VALUES (\'{fuel_type}\');')
                
                conn.commit()
            except Exception as error:
                conn.rollback()
                print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error}')
