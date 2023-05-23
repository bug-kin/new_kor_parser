class Proxy:
    url = (
        "https://proxy.webshare.io/api/v2/proxy/list/?mode=direct&page=1&page_size=100"
    )
    token = "9x3njmq5gcnpz8kg7hrugb5ciqkrmm8u68c7s9y6"


class MySQLConnection:
    host = "fm-mysql"
    user = "homestead"
    password = "xHQSMObK502iqzGfVTKQ"
    database = "homestead"
    engine = f"mysql+aiomysql://{user}:{password}@{host}:3306/{database}"


class SftpConnection:
    host = "fm-sftp"
    port = 22
    user = "sftp"
    password = "QXgxbjGdYp9qQra6nek2"


class Configuration:
    source = "bobaedream"
    proxy = Proxy()
    db = MySQLConnection()
    sftp = SftpConnection()


config = Configuration()
