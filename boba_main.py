import asyncio

from aiohttp import ClientSession

from Database import Database
from Parsers import BobaParser
from Utils import ProxyDispatcher, RequestDispatcher


async def main():
    async with ClientSession() as session:
        proxy_dispatcher = ProxyDispatcher()
        request_dispatcher = RequestDispatcher(session, proxy_dispatcher)
        database = Database()

        boba_parser = BobaParser(request_dispatcher, database)
        await boba_parser.parse()

if __name__ == "__main__":
    asyncio.run(main())
