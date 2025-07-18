from abc import ABC, abstractmethod
from typing import Union

import aiofiles
import sclib.asyncio


class ABCResource(ABC):

    @abstractmethod
    async def read(self) -> bytes:
        pass

class BytesResource(ABCResource):

    def __init__(self, data: bytes):
        self.data = data

    async def read(self) -> Union[bytes, str]:
        return self.data

class UrlResource(ABCResource):

    def __init__(self, url: str):
        self.url = url

    async def read(self) -> Union[bytes, str]:
        return await sclib.asyncio.get_resource(self.url)

class FileResource(ABCResource):

    def __init__(self, file_source: str):
        self.filepath = file_source

    async def read(self):
        async with aiofiles.open(self.filepath, "rb") as file:
            return await file.read()


