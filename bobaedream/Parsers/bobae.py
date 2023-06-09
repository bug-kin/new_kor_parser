import asyncio
import re
from datetime import datetime
from math import ceil
from pathlib import Path

import aiofiles
from bs4 import BeautifulSoup

ROOT_DIR = Path('share')
ROOT_DIR.mkdir(exist_ok=True)


class BobaParser:
    URL = 'https://www.bobaedream.co.kr/mycar/mycar_list.php?ot=second&view_size=40&gubun={type_}&carriage={body_}&page={page}'
    TYPES = ('I', 'K')
    BODY_TYPES = (
        '버스',
        '웨건',
        '준중형차',
        '대형차',
        '쿠페',
        '슈퍼카',
        '컨버터블',
        '소형차',
        'SUV',
        '리무진',
        'RV',
        '중형차',
        '밴',
        '캠핑카',
        '스포츠카',
        '승합차',
        '경차',
        '픽업',
        '트럭/화물',
        '해치백'
    )

    def __init__(self, request_dispatcher, database):
        self.request_dispatcher = request_dispatcher
        self.database = database
        self.body = None
        self.cars = []

    async def parse(self):
        for type_ in self.TYPES:
            for body_ in self.BODY_TYPES:
                self.body = body_
                page = 1
                pages = 1
                attempts = 2
                while True:
                    if page > pages:
                        break

                    try:
                        async with self.request_dispatcher.get(
                            self.URL.format(
                                type_=type_,
                                body_=body_,
                                page=page
                            )
                        ) as resp:
                            if resp.ok:
                                soup = BeautifulSoup(
                                    await resp.read(),
                                    'html.parser'
                                )
                                total, pages = (
                                    await self.get_total_records_and_pages(
                                        soup
                                    )
                                )

                            if total == 0:
                                break

                            await self.parse_cars(soup.find('div', id='listCont'))

                    except AttributeError:
                        if attempts == 0:
                            break

                        attempts -= 1

                    page += 1

                if self.cars:
                    await self.database.cars_processing(self.cars)
                    self.cars.clear()

    async def parse_cars(self, html):
        tasks = []
        for car in html.find_all('li', class_='product-item'):
            if car.find('p', class_='tit').text.strip().startswith('미니'):
                continue

            tasks.append(
                asyncio.create_task(
                    self.parse_car(car)
                )
            )

        self.cars += await asyncio.gather(*tasks)

    async def parse_car(self, html):
        car = {}
        car['source'] = 'bobaedream'
        car['id'] = int(re.search(
            r'no=(?P<carid>\d+)&',
            html.find('p', class_='tit').find('a')['href']
        ).group('carid'))

        print(f'{await self.time()} - Parsing car: [ {car["id"]} ]')

        cardir = ROOT_DIR.joinpath(f'bobaedream_{car["id"]}')
        cardir.mkdir(parents=True, exist_ok=True)

        car['preview'] = await self.extract_preview(
            html
            .find('div', class_='mode-cell thumb')
            .find('img')['src'],
            cardir
        ) if html.find('div', class_='mode-cell thumb').find('img') else None

        car['body_type'] = self.body
        car['mark'], car['model'], *car['grade'] = await self.extract_mark_model_grade(
            html.find('p', class_='tit').text
        )
        car['grade'] = ' '.join(car['grade']) if car['grade'] else None
        car['gearbox'] = html.find(
            'dd', class_='data-item').text
        car['transmission'] = await self.extract_transmission(
            html.find('dl', class_='data is-list').text
        )
        car['engine'] = await self.extract_engine_volume(
            car['grade']
        ) if car['grade'] else None
        car['year'] = await self.extract_year(
            html.find('div', class_='mode-cell year').text
        )
        car['fuel'] = html.find(
            'div', class_='mode-cell fuel').text.strip()
        car['mileage'] = await self.extract_mileage(
            html.find('div', class_='mode-cell km').text
        )
        car['price'] = await self.extract_price(
            html.find('div', class_='mode-cell price').text
        )
        return car

    async def extract_preview(self, string, car_dir):
        if 'cybercar' in string.lower():
            url = 'https:' + string.replace('thum5', 'img').replace('.jpg', '_1.jpg')
        else:
            url = 'https:' + string.replace('_s1', '')

        attempts = 2
        while True:
            try:
                async with self.request_dispatcher.get(url) as resp:
                    if resp.ok:
                        path_to_photo = car_dir.joinpath(Path(url).name)
                        async with aiofiles.open(path_to_photo, 'wb') as f:
                            await f.write(await resp.read())

                        return str(path_to_photo)

            except Exception as error:
                print(f'{await self.time()} - [ ERROR ] {error}')
                if attempts == 0:
                    return None

                await asyncio.sleep(3)
                attempts -= 1

    async def get_total_records_and_pages(self, html):
        total = int(
            html.find('span', id='tot').text
            .replace(",", "")
            .replace(".", "")
        )
        pages = ceil(total / 40)
        print(f'{await self.time()} - [ PAGES ] {pages} - [ TOTAL ] {total}')
        return total, pages

    @staticmethod
    async def extract_mark_model_grade(string):
        INCORRECT_WORDS = ('더', '뉴', '어메이징', '올', '디')
        return tuple(
            word
            for word in string.strip().split(' ')
            if word not in INCORRECT_WORDS
        )

    @staticmethod
    async def extract_transmission(string):
        TRANSMISSIONS = {
            'MR': 'RWD',
            'FR': 'RWD',
            'RR': 'RWD',
            'FF': 'FWD',
            '4WD': '4WD',
            '2WD': '2WD',
            'AWD': 'AWD',
        }
        if string := re.search(r'FF|FR|MR|RR|2WD|4WD|AWD', string):
            return TRANSMISSIONS[string.group(0)]

    @staticmethod
    async def extract_price(string):
        if price := re.fullmatch('\d+만원', string.strip().replace(',', '')):
            return int(re.sub(r'만원', '0000', price.group(0)))

    @staticmethod
    async def extract_year(string):
        if match := re.search(r"\((?P<Y>\d+)", string.strip()):
            return datetime.strptime(match.group('Y'), '%y').year

        if string.strip().endswith('00'):
            string = string.replace('00', '01')

        return datetime.strptime(string.strip(), '%y/%m').year

    @staticmethod
    async def extract_engine_volume(string):
        if match := re.search(r'\d{1,2}\.\d{1}', string.strip()):
            return int(float(match.group(0)) * 1_000)

    @staticmethod
    async def extract_mileage(string):
        mileage = string.strip()
        if '천' in mileage:
            mileage = mileage.replace('천', '000')

        if '만' in mileage:
            mileage = mileage.replace('만', '0000')

        if 'ml' in mileage:
            return int(int(mileage.replace('ml', '')) * 1.6)

        try:
            return int(mileage.replace('km', ''))
        except ValueError:
            return 0

    @staticmethod
    async def time():
        return datetime.now().strftime("%d-%m-%Y %H:%M:%S")
