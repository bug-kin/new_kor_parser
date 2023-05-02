import asyncio
from aiohttp import ClientSession
from Utils import ProxyDispatcher, RequestDispatcher
from Parsers import BobaParser, ChachaParser
from Database import Database


async def main():
    async with ClientSession() as session:
        proxy_dispatcher = ProxyDispatcher()
        request_dispatcher = RequestDispatcher(session, proxy_dispatcher)
        # database = Database()
        database = None

        chacha_parser = ChachaParser(request_dispatcher, database)
        boba_parser = BobaParser(request_dispatcher, database)

        await chacha_parser.parse()
        await boba_parser.parse()


if __name__ == "__main__":
    asyncio.run(main())
