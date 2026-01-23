import asyncio

from yt_dlp import YoutubeDL, _Params
from yt_dlp.extractor.common import _InfoDict


async def yt_dlp(opts: _Params, link: str, download=True) -> _InfoDict:
    return await asyncio.get_running_loop().run_in_executor(
        None,
        _yt_dlp,
        opts,
        link,
        download=download)


def _yt_dlp(opts: _Params, link: str, download=True) -> _InfoDict:
    with YoutubeDL(opts) as ytdl:
        return ytdl.extract_info(link, download=download)