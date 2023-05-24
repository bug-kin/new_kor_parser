class Proxy:
    url = (
        "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=100"
    )
    token = "9x3njmq5gcnpz8kg7hrugb5ciqkrmm8u68c7s9y6"


class MySQLConnection:
    host = "mysql"
    user = "homestead"
    password = "xHQSMObK502iqzGfVTKQ"
    database = "homestead"
    engine = f"mysql+aiomysql://{user}:{password}@{host}:3306/{database}"


class Configuration:
    source = "kbchachacha"
    proxy = Proxy()
    db = MySQLConnection()


config = Configuration()
