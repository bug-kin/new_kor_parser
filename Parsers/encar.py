import asyncio
import re
from datetime import datetime
from math import ceil
from pathlib import Path

import aiofiles
from aiohttp import ClientPayloadError

ROOT_DIR = Path('car_images')
ROOT_DIR.mkdir(exist_ok=True)


class EncarParser:
    LIMIT = 299
    PARAMS = {
        'http://api.encar.com/search/car/list/premium': {
            'expession': '(And.Hidden.N._.{type}._.{body})',
            'types': ('CarType.N', 'CarType.Y'),
            'body_type': ('Category.경차.', 'Category.소형차.', 'Category.준중형차.', 'Category.중형차.', 'Category.대형차.', 'Category.스포츠카.', 'Category.SUV.', 'Category.RV.', 'Category.경승합차.', 'Category.승합차.', 'Category.화물차.')
        },
        'http://api.encar.com/search/truck/list/premium': {
            'expession': '(And.{type}._.{body})',
            'types': ('Hidden.N',),
            'body_type': ('Form.카고(화물_)트럭.', 'Form.윙바디/탑.', 'Form.버스.', 'Form.덤프/건설/중기.', 'Form.크레인 형태.', 'Form.탱크로리.', 'Form.캠핑카/캠핑 트레일러.', 'Form.폐기/음식물수송.', 'Form.활어차.', 'Form.차량견인/운송.', 'Form.트렉터.', 'Form.트레일러.')
        },
    }

    def __init__(self, request_dispatcher, database):
        self.request_dispatcher = request_dispatcher
        self.database = database

    async def parse(self):
        for base_url, param in self.PARAMS.items():
            for type_ in param['types']:
                for body_ in param['body_type']:
                    count_url = f'{base_url}?count=true&q={param["expession"].format(type=type_, body=body_)}'
                    async with self.request_dispatcher.get(count_url) as resp:
                        if resp.ok:
                            res = await resp.json()
                            total, pages = await self.get_total_records_and_pages(res['Count'])

                    offset = 0
                    tasks = []
                    result = []
                    for page in range(1, pages+1):
                        if page != 1:
                            offset += self.LIMIT

                        data_url = f'{count_url}&sr=|ModifiedDate|{offset}|{self.LIMIT}'
                        if len(tasks) == 30:
                            result += await asyncio.gather(*tasks)
                            tasks.clear()

                        tasks.append(
                            asyncio.create_task(
                                self.get_cars(data_url, body_)
                            )
                        )

                    result += await asyncio.gather(*tasks)
                    tasks.clear()

                    result = {car['id']: car for batch in result for car in batch}

                    for car in result.values():
                        if len(tasks) == 30:
                            await asyncio.gather(*tasks)
                            tasks.clear()

                        tasks.append(
                            asyncio.create_task(
                                self.download_photo(car)
                            )
                        )

                    await asyncio.gather(*tasks)
                    tasks.clear()

                    self.database.insert_or_update_car(result.values())

    async def download_photo(self, car):
        car_dir = ROOT_DIR.joinpath(f'encar_{car["id"]}')
        car_dir.mkdir(parents=True, exist_ok=True)
        attempts = 2
        while True:
            try:
                async with self.request_dispatcher.get(
                    url=car['preview'],
                    params={
                        "impolicy": "widthRate",
                        "rw": 1024,
                        "cw": 1024,
                        "ch": 768,
                    }
                ) as resp:
                    if resp.ok:
                        path_to_photo = car_dir.joinpath(Path(car['preview']).name)
                        async with aiofiles.open(path_to_photo, 'wb') as f:
                            await f.write(await resp.read())

                        car['preview'] = str(path_to_photo)
                        return

            except ClientPayloadError as error:
                if attempts == 0:
                    break

                print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ERROR ] {error} - [ FILE ] {str(path_to_photo)}')
                asyncio.sleep(4)
                attempts -= 1

    async def get_cars(self, url, body_type):
        async with self.request_dispatcher.get(url) as resp:
            if resp.ok:
                res = await resp.json()
                result = []
                for car in res['SearchResults']:
                    if not car.get('Photos'):
                        continue

                    if car.get('Lease'):
                        continue

                    if car.get('ServiceCopyCar'):
                        if car.get('ServiceCopyCar') == 'ORIGINAL':
                            result.append(
                                {
                                    'source': 'encar',
                                    'id': int(car['Id']),
                                    'preview': await self.extract_preview(car.get('Photos')),
                                    'body_type': re.search(r'\.(?P<type>.+)\.', body_type).group('type'),
                                    'mark': car['Manufacturer'],
                                    'model': car['Model'],
                                    'grade': await self.extract_grade(car),
                                    'gearbox': car.get('Transmission'),
                                    'transmission': await self.extract_transmission(car.get("Badge")),
                                    'engine': await self.extract_engine_volume(car.get("Badge")),
                                    'year': int(car['FormYear']) if car.get('FormYear') else None,
                                    'fuel': car['FuelType'],
                                    'mileage': int(car['Mileage']),
                                    'price': int(car['Price'] * 10_000)
                                }
                            )

                        else:
                            continue

                    result.append(
                        {
                            'source': 'encar',
                            'id': int(car['Id']),
                            'preview': await self.extract_preview(car.get('Photos')),
                            'body_type': re.search(r'\.(?P<type>.+)\.', body_type).group('type'),
                            'mark': car['Manufacturer'],
                            'model': car['Model'],
                            # 'grade': f'{car.get("FormDetail")} {car.get("Capacity")} {car.get("Badge")}'.strip(),
                            'grade': await self.extract_grade(car),
                            'gearbox': car.get('Transmission'),
                            'transmission': await self.extract_transmission(
                                car.get("Badge")),
                            'engine': await self.extract_engine_volume(
                                car.get("Badge")),
                            'year': int(car['FormYear']) if car.get('FormYear') else None,
                            'fuel': car['FuelType'],
                            'mileage': int(car['Mileage']),
                            'price': int(car['Price'] * 10_000)
                        }
                    )

                return result

    @staticmethod
    async def extract_engine_volume(badge):
        if not badge:
            return None

        if match := re.search(r'\d{1,2}\.\d{1}', badge.strip()):
            return int(float(match.group(0)) * 1_000)

    @staticmethod
    async def extract_transmission(badge):
        if not badge:
            return None

        if match := re.search('(?P<transmission>AWD|RWD|FWD|2WD|4WD)', badge):
            return match.group('transmission')

    @staticmethod
    async def extract_grade(car):
        return f'{car.get("FormDetail")} {car.get("Capacity")} {car.get("Badge")} {car.get("BadgeDetail")}'.replace('None', '').strip()

    @staticmethod
    async def extract_preview(photo):
        if photo:
            return f'http://ci.encar.com/carpicture{photo[0]["location"]}'

    @staticmethod
    async def get_total_records_and_pages(total):
        print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ PAGES ] {ceil(total / 299)} - [ TOTAL ] {total}')
        return total, ceil(total / 299)
