import asyncio
from datetime import datetime
from pathlib import Path
from math import ceil


class EncarParser:
    LIMIT = 299
    PARAMS = {
        'http://api.encar.com/search/truck/list/premium': {
            'expession': '(And.{type}._.{body})',
            'types': ('Hidden.N',),
            'body_type': ('Form.카고(화물_)트럭.', 'Form.윙바디/탑.', 'Form.버스.', 'Form.덤프/건설/중기.', 'Form.크레인 형태.', 'Form.탱크로리.', 'Form.캠핑카/캠핑 트레일러.', 'Form.폐기/음식물수송.', 'Form.활어차.', 'Form.차량견인/운송.', 'Form.트렉터.', 'Form.트레일러.')
        },
        'http://api.encar.com/search/car/list/premium': {
            'expession': '(And.Hidden.N._.{type}._.{body})',
            'types': ('CarType.N', 'CarType.Y'),
            'body_type': ('Category.경차.', 'Category.소형차.', 'Category.준중형차.', 'Category.중형차.', 'Category.대형차.', 'Category.스포츠카.', 'Category.SUV.', 'Category.RV.', 'Category.경승합차.', 'Category.승합차.', 'Category.화물차.')
        },
    }

    def __init__(self, request_dispatcher, database):
        self.request_dispatcher = request_dispatcher
        self.database = database
        self.body_ = None
        self.cars = []

    async def parse(self):
        for base_url, param in self.PARAMS.items():
            for type_ in param['types']:
                for body_ in param['body_type']:
                    page = 1
                    pages = 1
                    offset = 0
                    while True:
                        if page > pages:
                            print('BREAK')
                            break

                        if page != 1:
                            offset += self.LIMIT

                        async with self.request_dispatcher.get(
                            url=f'{base_url}?count=true&q={param["expession"].format(type=type_, body=body_)}&sr=|ModifiedDate|{offset}|{self.LIMIT}'
                        ) as resp:
                            if resp.ok:
                                res = await resp.json()
                                total, pages = await self.get_total_records_and_pages(res['Count'])
                                print()

                        page += 1

                    print()

    @staticmethod
    async def get_total_records_and_pages(total):
        print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ PAGES ] {ceil(total / 299)} - [ TOTAL ] {total}')
        return total, ceil(total / 299)
