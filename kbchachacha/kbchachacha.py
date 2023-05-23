import asyncio
from datetime import datetime
from time import time

from aiohttp import ClientSession
from Parsers.chacha import ChachaParser
from Utils.proxy_dispatcher import ProxyDispatcher
from Utils.request_dispatcher import RequestDispatcher
from Database.sa_database import Database


async def main():
    proxy_dispatcher = ProxyDispatcher()
    async with ClientSession() as session:
        request_dispatcher = RequestDispatcher(
            session=session,
            proxy_dispatcher=proxy_dispatcher
        )
        database = Database()

        parser = ChachaParser(
            request_dispatcher=request_dispatcher,
            database=database
        )
        await parser.parse()
        print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ DONE ] Parsing done')


if __name__ == '__main__':
    start = time()
    asyncio.run(main=main())
    print(f'-- {time() - start} s --')
