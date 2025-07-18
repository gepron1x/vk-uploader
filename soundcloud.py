import asyncio
from typing import AnyStr, Optional, Union

import aiohttp
import sclib
from sclib.asyncio import SoundcloudAPI, Track, Playlist
from vkbottle import PhotoMessageUploader, Bot, ABCAPI, BaseUploader, NotRule
from vkbottle.bot import Message
from vkbottle.dispatch.rules.base import RegexRule, AttachmentTypeRule, TextRule
from vkbottle.framework.labeler import BotLabeler

import config
import vk_albums
from music_resource import UrlResource, BytesResource
from rules import UrlRule
from uploaders import AudioToUpload, UploadedAudio
from userbots import audio_uploader, user, batch_audio_uploader, album_cover_uploader

labeler = BotLabeler()

async def redirect(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return response.url or url

@labeler.message(UrlRule("soundcloud.com"), NotRule(AttachmentTypeRule("link")))
async def soundcloud(message: Message):
    await _soundcloud(message, message.text)

@labeler.message(RegexRule(r'Listen to .+ by .+ on #SoundCloud\s+(https?://\S+)'), NotRule(AttachmentTypeRule("link")))
async def soundcloud_re(message: Message, match: tuple[AnyStr]):
    await _soundcloud(message, match[0])

async def _soundcloud(message: Message, url: str):
    api = SoundcloudAPI()
    url = await redirect(url)
    obj = await api.resolve(url)
    if obj is None:
        await message.reply("По ссылке ничего не найдено.")
        return
    if type(obj) is Track:
        await reply_track(message, obj)
    elif type(obj) is Playlist:
        await reply_playlist(message, obj)
    else:
        await message.reply("По ссылке ничего не найдено.")


async def reply_track(message: Message, track: Track):
    attachments = await asyncio.gather(upload_soundcloud_track(track),
                                        upload_soundcloud_cover(track, message))
    await message.reply("Успешно загружено.", attachment=[a for a in attachments if a is not None])

async def reply_playlist(message: Message, playlist: Playlist):
    await message.reply("Успешно загружено.", attachment=await upload_soundcloud_playlist(playlist))

async def upload_soundcloud_track(track: Track) -> str:
    file_source = await sclib.asyncio.get_resource(await track.get_stream_url())
    return await audio_uploader.upload(track.artist, track.title, file_source)

async def download_artwork(obj: Union[Track, Playlist]) -> Optional[bytes]:
    if not obj.artwork_url:
        return None
    url = obj.artwork_url.replace('large', 't500x500')
    return await sclib.asyncio.get_resource(url)

async def upload_soundcloud_cover(track: Track, message: Message) -> Optional[str]:
    file_source = await download_artwork(track)
    if not file_source:
        return None
    photo_uploader = PhotoMessageUploader(message.ctx_api)
    return await photo_uploader.upload(file_source, peer_id=message.peer_id)

async def upload_soundcloud_playlist(playlist: Playlist) -> str:
    album = await vk_albums.create_album(config.PLAYLIST_OWNER_ID, playlist.title)
    audio_to_upload = [AudioToUpload(UrlResource(await track.get_stream_url()),
                                             track.artist,
                                             track.title) for track in playlist.tracks]
    audio_to_upload.reverse()
    uploaded = await batch_audio_uploader.upload_batch(audio_to_upload)
    await album.add_audio(uploaded)
    art = await download_artwork(playlist)
    if not art and playlist.tracks:
        art = await download_artwork(playlist.tracks[0])
    if art:
        await album.set_cover(BytesResource(art))
    return album.as_attachment()