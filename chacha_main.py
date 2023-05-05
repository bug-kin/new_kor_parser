import asyncio
from datetime import datetime
from time import time

from aiohttp import ClientSession

from Database import Database
from Parsers import ChachaParser
from Utils import ProxyDispatcher, RequestDispatcher


async def main():
    async with ClientSession() as session:
        proxy_dispatcher = ProxyDispatcher()
        request_dispatcher = RequestDispatcher(session, proxy_dispatcher)
        database = Database()

        chacha_parser = ChachaParser(request_dispatcher, database)
        await chacha_parser.parse()
        print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ DONE ] Parsing done')

if __name__ == "__main__":
    start = time()
    asyncio.run(main())
    print(f'-- {time() - start} s --')
