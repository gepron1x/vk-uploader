import os
from dataclasses import dataclass
from urllib.parse import ParseResult
from vkbottle import Keyboard, Callback, NotRule
from vkbottle.bot import Message, MessageEvent
from vkbottle.dispatch.rules.base import RegexRule, AttachmentTypeRule
from vkbottle.framework.labeler import BotLabeler
from vkbottle_types.events import GroupEventType

from async_dlp import yt_dlp
from rules import UrlRule
from userbots import video_uploader, audio_uploader

TEMPORARY_PATH = "/tmp/vk-music-downloader"

YT_DLP_AUDIO_OPTS = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}

YT_DLP_VIDEO_OPTS = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
}
YOUTUBE_REGEX = r"^((?:https?:)?\/\/)?((?:www|m)\.)?((?:youtube\.com|youtu.be))(\/(?:[\w\-]+\?v=|embed\/|v\/)?)([\w\-]+)(\S+)?$"

labeler = BotLabeler()


@dataclass
class YTDlpInfo:
    title: str
    author: str
    filepath: str


@labeler.message(UrlRule("youtube.com", "youtu.be"), NotRule(AttachmentTypeRule("link")))
async def youtube(message: Message):
    keyboard = Keyboard(inline=True, one_time=False)
    keyboard.add(Callback("Аудио", {"type": "youtube_audio", "link": message.text}))
    keyboard.add(Callback("Видео", {"type": "youtube_video", "link": message.text}))
    await message.answer("YouTube", keyboard=keyboard.get_json(), reply_to=message.id)


@labeler.raw_event(GroupEventType.MESSAGE_EVENT, MessageEvent)
async def yt_keyboard(event: MessageEvent):
    payload = event.payload
    if "type" not in payload:
        return
    link = payload["link"]
    await event.show_snackbar("Начинаем загрузку!")
    video = payload["type"] == "youtube_video"
    if video:
        attachment = await _youtube_video(link)
    else:
        attachment = await _youtube_audio(link)
    message = "Успешно загружено."
    if video:
        message += f"\nhttps://vk.com/{attachment}" # dirty hack, fuck vkontakte
    await event.send_message(message, attachment=attachment)


async def _youtube_audio(link: str) -> str:
    info = await download_from_youtube(link, YT_DLP_AUDIO_OPTS)
    try:
        attachment = await audio_uploader.upload(file_source=info.filepath,
                                       artist=info.author,
                                       title=info.title)
    finally:
        os.remove(info.filepath)
    return attachment


async def _youtube_video(link: str) -> str:
    info = await download_from_youtube(link, YT_DLP_VIDEO_OPTS)
    try:
        attachment = await video_uploader.upload(file_source=info.filepath,
                                           name=info.title, description=f"Original: {link}\n"
                                                                        f"Author: {info.author}"
                                                                        f"@objectwebasm",
                                           wallpost=True)
    finally:
        os.remove(info.filepath)
    return attachment


async def download_from_youtube(link: str, opts: dict) -> YTDlpInfo:
    opts = {**opts,
            "outtmpl": f"{TEMPORARY_PATH}/%(extractor_key)s/%(extractor)s-%(id)s-%(title)s.%(ext)s",
            "cookiefile": "cookies.txt"
            }
    result = await yt_dlp(opts, link)
    return YTDlpInfo(result['title'],
                     result['uploader'],
                     result['requested_downloads'][0]['filepath'])
