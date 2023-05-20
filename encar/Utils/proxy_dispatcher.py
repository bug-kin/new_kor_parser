from random import choice

import requests

from configs import config


class ProxyDispatcher:
    def __init__(self):
        self.proxies = self.get_proxies()

    def get_proxies(self):
        with requests.get(
            url=config.proxy.url,
            headers={"Authorization": f"Token {config.proxy.token}"},
        ) as resp:
            if resp.ok:
                webshare_response = resp.json()
                return [
                    f'http://{data["username"]}:{data["password"]}@{data["proxy_address"]}:{data["port"]}'
                    for data in webshare_response["results"]
                ]

    async def get_proxy(self):
        return choice(self.proxies)
