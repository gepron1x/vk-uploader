import asyncio

from yt_dlp import YoutubeDL

async def yt_dlp(opts: dict, link: str) -> dict:
    return await asyncio.get_running_loop().run_in_executor(None, _yt_dlp, opts, link)


def _yt_dlp(opts: dict, link: str) -> dict:
    with YoutubeDL(opts) as ytdl:
        return ytdl.extract_info(link)