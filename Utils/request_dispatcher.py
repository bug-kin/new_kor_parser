import asyncio
from datetime import datetime
from random import randint

from aiohttp import ClientSession, ClientTimeout
from fake_useragent import FakeUserAgent


class _SafeRequestContextManager:
    def __init__(
        self,
        session,
        proxy_dispatcher,
        method,
        url,
        **kwargs,
    ):
        self.session = session
        self.proxy_dispatcher = proxy_dispatcher
        self.url = url
        self.method = method
        self.kwargs = kwargs
        self.agent = FakeUserAgent()
        self.proxy = 'http://mzrgytyk-rotate:vc6crg3txb76@p.webshare.io:80/'
        self.timeout = ClientTimeout(120)

    async def __aenter__(self):
        attempt = 1
        while True:
            if 'headers' in self.kwargs.keys():
                self.kwargs['headers']['User-Agent'] = self.agent.random
            else:
                self.kwargs['headers'] = {'User-Agent': self.agent.random}

            try:
                proxy = await self.proxy_dispatcher.get_proxy()
                print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ URL ] {self.url} - [ {proxy} ]')
                await asyncio.sleep(randint(1, 2))
                result = await self.session.request(
                    self.method,
                    self.url,
                    proxy=proxy,
                    verify_ssl=False,
                    timeout=self.timeout,
                    **self.kwargs
                )
                return result

            except RuntimeError:
                self.session = ClientSession()

            except Exception as error:
                if attempt == 3:
                    return

                print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ ATTEMPT ] {attempt} - [ ERROR ] {error} - [ URL ] {self.url}')
                attempt += 1
                await asyncio.sleep(randint(2, 3))

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, "res"):
            self.res.close()


class RequestDispatcher:
    def __init__(
        self,
        session,
        proxy_dispatcher
    ):
        self.session = session
        self.proxy_dispatcher = proxy_dispatcher

    def request(self, method, url, **kwargs):
        return _SafeRequestContextManager(
            self.session,
            self.proxy_dispatcher,
            method,
            url,
            **kwargs,
        )

    def get(self, url, **kwargs):
        return self.request('GET', url, **kwargs)

    def post(self, url, **kwargs):
        return self.request('POST', url, **kwargs)
