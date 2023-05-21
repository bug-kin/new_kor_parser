class Proxy:
    url = (
        "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=100"
    )
    token = "9x3njmq5gcnpz8kg7hrugb5ciqkrmm8u68c7s9y6"


class Connection:
    host = "pepe.foundation"
    user = "homestead"
    password = "homestead"
    database = "homestead"
    engine = f"mysql+aiomysql://{user}:{password}@{host}/{database}"


class Configuration:
    source = "bobaedream"
    proxy = Proxy()
    connection = Connection()


config = Configuration()
