import asyncio
from datetime import datetime
from pathlib import Path

import asyncssh
from configs import config


class Sftp:
    def __init__(self):
        self.connection = asyncssh.connect(
            host=config.sftp.host,
            port=config.sftp.port,
            username=config.sftp.user,
            password=config.sftp.password
        )
        self.root_dir = Path('share')

    async def upload(self, photo_path):
        print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TRANSFER ] Image {photo_path.name} transering')
        async with self.connection as connection:
            async with connection.start_sftp_client() as sftp:
                path_to_file = self.root_dir.joinpath(photo_path.parent.stem)
                if not await sftp.exists(path_to_file):
                    await sftp.mkdir(str(path_to_file))

                path_to_file = path_to_file.joinpath(photo_path.name)
                await sftp.put(str(photo_path), str(path_to_file))

        print(f'{datetime.now().strftime("%d-%m-%Y %H:%M:%S")} - [ TRANSFER ] Image {photo_path.name} transfered')
        return str(path_to_file)
