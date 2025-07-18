from collections.abc import Iterable
from dataclasses import dataclass

from vkbottle import BaseUploader

from music_resource import ABCResource
from uploaders import UploadedAudio
from userbots import user, album_cover_uploader


@dataclass
class VkAlbum:
    owner_id: int
    playlist_id: int
    title: str

    async def set_cover(self, resource: ABCResource):
        await album_cover_uploader.raw_upload(owner_id=self.owner_id,
                                              playlist_id=self.playlist_id,
                                              file_source=await resource.read())

    async def add_audio(self, audios: Iterable[UploadedAudio]):
        uploaded = [a.as_playlist_entry() for a in audios]
        await user.api.request("audio.addToPlaylist",
                               {"owner_id": self.owner_id,
                                "playlist_id": self.playlist_id,
                                "audio_ids": uploaded})

    def as_attachment(self):
        return BaseUploader.generate_attachment_string("audio_playlist",
                                                       self.owner_id,
                                                       self.playlist_id)

    def __str__(self):
        return self.as_attachment()


async def create_album(owner_id: int, title: str) -> VkAlbum:
    result = await user.api.request("audio.createPlaylist", {"title": title,
                                                             "owner_id": owner_id})  # TODO: make this configurable
    result = result["response"]
    owner_id, playlist_id = result["owner_id"], result["id"]
    return VkAlbum(owner_id, playlist_id, title)

