import asyncio
from datetime import datetime
from time import time as t

from aiohttp import ClientSession
from Database.sa_database import Database
from Parsers.encar import EncarParser
from Utils.proxy_dispatcher import ProxyDispatcher
from Utils.request_dispatcher import RequestDispatcher


async def time():
    return datetime.now().strftime("%d-%m-%Y %H:%M:%S")


async def main():
    proxy_dispatcher = ProxyDispatcher()
    async with ClientSession() as session:
        request_dispatcher = RequestDispatcher(
            session=session, proxy_dispatcher=proxy_dispatcher
        )
        database = Database()

        parser = EncarParser(
            request_dispatcher=request_dispatcher,
            database=database
        )
        try:
            await database.update_monitoring(None)
            await parser.parse()
            await database.update_monitoring(True)
        except Exception as error:
            print(f'{await time()} - [ ERROR ] {error}')
            await database.update_monitoring(False)


if __name__ == "__main__":
    start = t()
    asyncio.run(main=main())
    print(f"-- {t() - start} s --")
