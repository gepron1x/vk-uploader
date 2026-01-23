import asyncio
from typing import Optional
from urllib.parse import ParseResult

from vkbottle import NotRule, PhotoMessageUploader
from vkbottle.bot import Message
from vkbottle.dispatch.rules.base import AttachmentTypeRule
from vkbottle.framework.labeler import BotLabeler

import config
import vk_albums
from async_dlp import yt_dlp
from music_resource import UrlResource
from rules import UrlRule
from uploaders import AudioToUpload
from userbots import batch_audio_uploader

labeler = BotLabeler()

@labeler.message(UrlRule("bandcamp.com"), NotRule(AttachmentTypeRule("link")))
async def bandcamp(message: Message):
    url = message.text
    info = await yt_dlp({}, url, download=False)
    if info.get('_type', None) == 'playlist': # Upload playlist
        attachments = [await upload_playlist(info)]
    else: # Upload track
        attachments = await asyncio.gather(upload_thumbnail(info, message),
                                          upload_audio(info))
    await message.reply("Успешно загружено",
                        attachment=[a for a in attachments if a is not None])




def map_entry_to_audio(entry) -> AudioToUpload:
    track = entry.get('track', 'untitled')
    artist = entry.get('artist', 'unknown')
    download_url = entry['url']
    return AudioToUpload(title=track,
                         artist=artist,
                         file_source=UrlResource(download_url)
                         )

async def upload_audio(info: dict):
    audio = map_entry_to_audio(info)
    uploaded = await batch_audio_uploader.upload_single(audio)
    return uploaded.as_attachment()

async def upload_thumbnail(info: dict, message: Message) -> Optional[str]:
    thumbnail = info.get('thumbnail')
    if not thumbnail:
        return None
    resource = UrlResource(thumbnail)
    data = await resource.read()
    if not data:
        return None
    photo_uploader = PhotoMessageUploader(message.ctx_api)
    return await photo_uploader.upload(data, peer_id=message.peer_id)


async def upload_playlist(info: dict) -> str:
    playlist_title = info.get("title", "Untitled")
    entries = info.get("entries", [])
    thumbnail_url = entries[0].get("thumbnail", None) if entries else None

    audios = await batch_audio_uploader.upload_batch(
        [map_entry_to_audio(entry) for entry in entries]
    )


    album = await vk_albums.create_album(config.PLAYLIST_OWNER_ID, playlist_title)
    await album.add_audio(audios[::-1])
    if thumbnail_url:
        await album.set_cover(UrlResource(thumbnail_url))
    return album.as_attachment()








