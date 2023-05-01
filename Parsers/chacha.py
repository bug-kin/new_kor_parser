import asyncio
import re
from datetime import datetime
from math import ceil
from pathlib import Path

from aiohttp import ClientSession
from bs4 import BeautifulSoup

from Utils import RequestDispatcher

ROOT_DIR = Path('car_images')
ROOT_DIR.mkdir(exist_ok=True)

class ChachaParser:
    FILTER_URL = 'https://www.kbchachacha.com/public/search/optionSale.json'
    URL = 'https://www.kbchachacha.com/public/search/list.empty?pageSize=6&useCode={code}&page={page}'
    JSON_URL = 'https://www.kbchachacha.com/public/car/common/recent/car/list.json?gotoPage=1&pageSize=1&carSeqVal={car_id}'
    BODY_TYPES = {
        '002001': '경차',
        '002002': '소형',
        '002003': '준중형',
        '002004': '중형',
        '002005': '대형',
        '002006': '스포츠카',
        '002007': 'RV',
        '002008': 'SUV',
        '002009': '승합',
        '002010': '버스',
        '002011': '트럭',
    }

    def __init__(self, request_dispatcher, database):
        self.request_dispatcher = request_dispatcher
        self.database = database
        self.cars = {}
    
    async def parse(self):
        await self.get_all_cars()
        tasks = []
        for car in self.cars.values():
            if len(tasks) == 40:
                await asyncio.gather(*tasks)
                tasks.clear()
            
            tasks.append(asyncio.create_task(self.parse_car(car)))
        
        await asyncio.gather(*tasks)
        tasks.clear()
        
        self.database.insert_or_update_car(self.cars.values())
        
    
    
    async def parse_car(self, car):
        async with self.request_dispatcher.post(
            self.JSON_URL.format(
                car_id=car['id']
            )
        ) as resp:
            if resp.ok:
                json = await resp.json()
                if not json['list']:
                    print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ SOLD ] - Car {car["id"]} sold out.')
                    return
                
                json = json['list'][0]
                car['mark'] = json['makerName']
                car['model'] = json['className']
                car['grade'] = f'json["modelName"] + json["gradeName"]'.strip()
                car['gearbox'] = None
                
                if match := re.search('(?P<transmission>AWD|RWD|FWD|2WD|4WD)', car['grade']):
                    car['transmission'] = match.group('transmission')
                else:
                    car['transmission'] = None
                
                if match := re.search(r'(?P<vol>\d{1,2}\.\d{1})', car['grade']):
                    car['engine'] = int(float(match.group('vol')) * 1_000)
                else:
                    car['engine'] = None
                
                car['year'] = int(json['yymm'])
                car['fuel'] = None
                car['mileage'] = json['km']
                car['price'] = json['sellAmt'] * 10_000
            
        

    async def get_all_cars(self):
        async with self.request_dispatcher.get(
            self.FILTER_URL
        ) as resp:
            if resp.ok:
                all_filters = await resp.json()
                use_code_filter = all_filters['optionSale']['result']['useCode']
                cars = []
                for code, name in self.BODY_TYPES.items():
                    total, pages = await self.get_total_records_and_pages(code, use_code_filter)
                    if not pages:
                        continue
                    
                    tasks = []
                    for page in range(1, pages + 1):
                        if len(tasks) == 40:
                            cars += await asyncio.gather(*tasks)
                            tasks.clear()
                        
                        tasks.append(
                            asyncio.create_task(self.get_cars_per_page(code, page, name))
                        )
                    
                    cars += await asyncio.gather(*tasks)
                    tasks.clear()
                
                await self.convert_to_one_dictionary(cars)

    async def convert_to_one_dictionary(self, cars):
        for batch in cars:
            if not batch:
                continue

            self.cars.update(batch)

    async def get_cars_per_page(self, code, page, body_type):
        async with self.request_dispatcher.get(
            self.URL.format(code=code, page=page)
        ) as resp:
            soup = BeautifulSoup(await resp.read(), 'html.parser')
            general_cars = soup.find('div', class_='generalRegist')
            return {
                int(car['data-car-seq']): {
                    'id': int(car['data-car-seq']),
                    'preview': await self.download_photo(
                        car.find('img')['src'], int(car['data-car-seq'])),
                    'body_type': body_type,
                }
                for car in general_cars.find_all('div', class_='area')
            }
    
    async def download_photo(self, url, car_id):
        car_dir = ROOT_DIR.joinpath(f'kbchachacha_{car_id}')
        car_dir.mkdir(parents=True, exist_ok=True)
        
        url = url.replace('?width=360', '')
        async with self.request_dispatcher.get(url) as resp:
            if resp.ok:
                path_to_photo = car_dir.joinpath(Path(url).name)
                with open(path_to_photo, 'wb') as f:
                    f.write(await resp.read())
                
                return str(path_to_photo)

    @staticmethod
    async def get_total_records_and_pages(code, filter_):
        total = filter_.get(code)
        pages = ceil(total / 110)
        if pages > 80:
            pages = 80
        print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ PAGES ] {pages} - [ TOTAL ] {total}')
        return total, pages
