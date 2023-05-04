import asyncio
from aiohttp import ClientSession
from Utils import ProxyDispatcher, RequestDispatcher
from Parsers import EncarParser
from Database import Database


async def main():
    async with ClientSession() as session:
        proxy_dispatcher = ProxyDispatcher()
        request_dispatcher = RequestDispatcher(session, proxy_dispatcher)
        database = Database()

        encar_parser = EncarParser(request_dispatcher, database)
        await encar_parser.parse()


if __name__ == "__main__":
    asyncio.run(main())
