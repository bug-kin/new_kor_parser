import asyncio
import re
from datetime import datetime
from math import ceil
from pathlib import Path

import aiofiles
from bs4 import BeautifulSoup

ROOT_DIR = Path("share")
ROOT_DIR.mkdir(exist_ok=True)


class ChachaParser:
    FILTER_URL = "https://www.kbchachacha.com/public/search/optionSale.json"
    URL = "https://www.kbchachacha.com/public/search/list.empty?pageSize=6&useCode={code}&page={page}"
    JSON_URL = "https://www.kbchachacha.com/public/car/common/recent/car/list.json?gotoPage=1&pageSize=1&carSeqVal={car_id}"
    BODY_TYPES = {
        "002001": "경차",
        "002002": "소형",
        "002003": "준중형",
        "002004": "중형",
        "002005": "대형",
        "002006": "스포츠카",
        "002007": "RV",
        "002008": "SUV",
        "002009": "승합",
        "002010": "버스",
        "002011": "트럭",
    }

    def __init__(self, request_dispatcher, database):
        self.request_dispatcher = request_dispatcher
        self.database = database

    async def parse(self):
        async with self.request_dispatcher.get(self.FILTER_URL) as resp:
            if resp.ok:
                all_filters = await resp.json()
                all_filters = all_filters["optionSale"]["result"]["useCode"]
                for code, name in self.BODY_TYPES.items():
                    if not (
                        cars := await self.parse_cars_for_category(
                            all_filters, code, name
                        )
                    ):
                        continue

                    tasks = []
                    for car in cars.values():
                        if len(tasks) == 30:
                            await asyncio.gather(*tasks)
                            tasks.clear()

                        tasks.append(asyncio.create_task(self.parse_car(car)))

                    await asyncio.gather(*tasks)
                    tasks.clear()

                    await self.database.cars_processing(list(cars.values()))

    async def parse_car(self, car):
        attempts = 2
        while True:
            try:
                async with self.request_dispatcher.post(
                    self.JSON_URL.format(car_id=car["id"])
                ) as resp:
                    if resp.ok:
                        json = await resp.json()
                        if not json["list"]:
                            print(
                                f'{await self.time()} - [ SOLD ] Car {car["id"]} sold out.'
                            )
                            car["deleted_at"] = True
                            return

                        json = json["list"][0]
                        car["mark"] = json["makerName"]
                        car["model"] = json["className"]
                        car["grade"] = f'{json["modelName"]} {json["gradeName"]}'.strip()
                        car["gearbox"] = None
                        car["preview"] = await self.download_photo(
                            car.get("preview"), car["id"]
                        )

                        if match := re.search(
                            "(?P<transmission>AWD|RWD|FWD|2WD|4WD)", car["grade"]
                        ):
                            car["transmission"] = match.group("transmission")
                        else:
                            car["transmission"] = None

                        if match := re.search(r"(?P<vol>\d{1,2}\.\d{1})", car["grade"]):
                            car["engine"] = int(float(match.group("vol")) * 1_000)
                        else:
                            car["engine"] = None

                        car["year"] = int(json["yymm"])
                        car["fuel"] = None
                        car["mileage"] = json["km"]
                        car["price"] = json["sellAmt"] * 10_000
                        return

            except Exception as error:
                print(f'{await self.time()} - [ ERROR ] {error}')
                if attempts == 0:
                    car["deleted_at"] = True
                    return

                await asyncio.sleep(2)
                attempts -= 1

    async def download_photo(self, url, car_id):
        car_dir = ROOT_DIR.joinpath(f"kbchachacha_{car_id}")
        car_dir.mkdir(parents=True, exist_ok=True)
        attempts = 2
        while True:
            try:
                async with self.request_dispatcher.get(url) as resp:
                    if resp.ok:
                        path_to_photo = car_dir.joinpath(Path(url).name)
                        async with aiofiles.open(path_to_photo, "wb") as f:
                            await f.write(await resp.read())

                        return str(path_to_photo)

            except Exception as error:
                if attempts == 0:
                    return None

                print(f'{await self.time()} - [ ERROR ] {error}')
                await asyncio.sleep(3)
                attempts -= 1

    async def parse_cars_for_category(self, filter, code, name):
        cars = []
        total = filter.get(code)
        pages = await self.calculate_pages(total)
        if not pages:
            return

        tasks = []
        for page in range(1, pages + 1):
            if len(tasks) == 30:
                cars += await asyncio.gather(*tasks)
                tasks.clear()

            tasks.append(asyncio.create_task(self.parse_car_on_page(code, name, page)))

        cars += await asyncio.gather(*tasks)
        tasks.clear()

        return {k: v for batch in cars if batch for k, v in batch.items()}

    async def parse_car_on_page(self, code, body_type, page):
        try:
            async with self.request_dispatcher.get(
                self.URL.format(code=code, page=page)
            ) as resp:
                soup = BeautifulSoup(await resp.read(), "html.parser")
                general_cars = soup.find("div", class_="generalRegist")
                return {
                    int(car["data-car-seq"]): {
                        "source": "kbchachacha",
                        "id": int(car["data-car-seq"]),
                        "preview": car.find("img")["src"].replace("?width=360", ""),
                        "body_type": body_type,
                    }
                    for car in general_cars.find_all("div", class_="area")
                }
        except AttributeError as error:
            print(f'{await self.time()} - [ ATTRIBUTE ERROR ] {error}')
            return None

    async def calculate_pages(self, total):
        pages = ceil(total / 50)
        if pages > 60:
            pages = 60

        print(f'{await self.time()} - [ TOTAL PAGES ] {pages}')
        return pages

    @staticmethod
    async def time():
        return datetime.now().strftime("%d-%m-%Y %H:%M:%S")
