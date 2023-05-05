from random import choice

import requests


class ProxyDispatcher:
    def __init__(self):
        self.proxies = self.get_proxies()

    def get_proxies(self):
        with requests.get(
                url='https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=100',
                headers={'Authorization': 'Token 9x3njmq5gcnpz8kg7hrugb5ciqkrmm8u68c7s9y6'}
        ) as resp:
            if resp.ok:
                webshare_response = resp.json()
                return [
                    f'http://{data["username"]}:{data["password"]}@{data["proxy_address"]}:{data["port"]}'
                    for data in webshare_response['results']
                ]

    async def get_proxy(self):
        return choice(self.proxies)
