import asyncio
from time import time

from aiohttp import ClientSession
from Parsers.bobae import BobaParser
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

        parser = BobaParser(
            request_dispatcher=request_dispatcher,
            database=database
        )

        try:
            await database.update_monitoring(None)
            await parser.parse()
            await database.update_monitoring(True)
        except Exception:
            await database.update_monitoring(False)


if __name__ == '__main__':
    start = time()
    asyncio.run(main=main())
    print(f'-- {time() - start} s --')
