import asyncio
from aiohttp import ClientSession
from Utils import RequestDispatcher
from Parsers import BobaParser, ChachaParser
from Database import Database


async def main():
    async with ClientSession() as session:
        request_dispatcher = RequestDispatcher(session)
        # database = Database()
        database = None

        boba_parser = BobaParser(request_dispatcher, database)
        chacha_parser = ChachaParser(request_dispatcher, database)
        
        await chacha_parser.parse()
        await boba_parser.parse()


if __name__ == "__main__":
    asyncio.run(main())