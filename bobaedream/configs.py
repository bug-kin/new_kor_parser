import os


class Proxy:
    url = (
        "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=100"
    )
    token = os.getenv('PROXY_TOKEN')


class MySQLConnection:
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    database = os.getenv('DB_NAME')
    user = os.getenv('DB_USER')
    password = os.getenv('DB_PSWD')
    engine = f"mysql+aiomysql://{user}:{password}@{host}:{port}/{database}"


class Configuration:
    source = "bobaedream"
    proxy = Proxy()
    db = MySQLConnection()


config = Configuration()
