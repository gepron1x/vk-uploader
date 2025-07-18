import urllib
from typing import Union, Optional
from urllib.parse import urlparse, ParseResult

from vkbottle import ABCRule
from vkbottle.bot import Message


def parse_url(text: str) -> Optional[ParseResult]:
    try:
        url = urlparse(text)
        return url
    except ValueError:
        return None

class UrlRule(ABCRule[Message]):

    def __init__(self, *available_netloc):
        self.available_netloc = available_netloc

    async def check(self, event: Message) -> Union[dict, bool]:
        url = parse_url(event.text)
        if not url:
            return False
        if url.netloc in self.available_netloc:
            return {"url": url}
        return False