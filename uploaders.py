import asyncio
import random
from collections.abc import Iterable
from dataclasses import dataclass
from io import BytesIO
from typing import Union, Optional

from vkbottle import AudioUploader, VKAPIError
from vkbottle.tools.uploader.base import BaseUploader

from music_resource import ABCResource


@dataclass
class AudioToUpload:
    file_source: ABCResource
    artist: str
    title: str

@dataclass
class UploadedAudio:
    owner_id: int
    audio_id: int
    access_key: Optional[str]

    def as_attachment(self):
        return BaseUploader.generate_attachment_string("audio",
                                                       self.owner_id,
                                                       self.audio_id,
                                                       self.access_key)

    def as_playlist_entry(self):
        return f"{self.owner_id}_{self.audio_id}"


class BatchAudioUploader:

    def __init__(self, audio_uploader: AudioUploader):
        self.uploader = audio_uploader

    async def upload_batch(self, audios: Iterable[AudioToUpload]) -> list[UploadedAudio]:
        server = await self.uploader.get_server()
        result = []
        for idx, audio in enumerate(audios, 1):
            print(f"Uploading track {idx}")
            try:
                uploaded_audio = await self.upload(audio, server)
            except VKAPIError[100] as e:
                if "server is undefined" in str(e):
                    print("We got server undefined!")
                    await asyncio.sleep(random.randint(10, 20))
                    server = await self.uploader.get_server()
                    uploaded_audio = await self.upload(audio, server)
                else:
                    raise e
            print(f"Done track {idx}")
            result.append(uploaded_audio)
            await asyncio.sleep(random.randint(2, 5))
        return result

    async def get_server(self):
        return await self.uploader.get_server()


    async def upload_single(self, audio: AudioToUpload) -> UploadedAudio:
        return await self.upload(audio, await self.uploader.get_server())

    async def upload(self, audio: AudioToUpload, server: dict) -> UploadedAudio:
        data = await audio.file_source.read()
        file = self.uploader.get_bytes_io(data)
        uploader = await self.uploader.upload_files(server["upload_url"], {"file": file})
        audio = (await self.uploader.api.request(
                    "audio.save",
                    {"artist": audio.artist, "title": audio.title, **uploader},
                ))["response"]
        return UploadedAudio(await self.uploader.get_owner_id(**audio), audio["id"], audio.get("access_key"))


class AlbumCoverUploader(BaseUploader):

    @property
    def attachment_name(self) -> str:
        return "image.jpg"

    async def raw_upload(self, owner_id: int, playlist_id: int, file_source):
        server = await self.get_server(owner_id=owner_id, playlist_id=playlist_id)
        data = await self.read(file_source)
        file = self.get_bytes_io(data)
        result = await self.upload_files(server['upload_url'], {"file": file})
        return await self.api.request("audio.setPlaylistCoverPhoto", {**result})

    async def get_server(self, **kwargs) -> dict:
        return (await self.api.request("photos.getAudioPlaylistCoverUploadServer", kwargs))["response"]



