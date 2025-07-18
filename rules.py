import urllib
from typing import Union, Optional
from urllib.parse import urlparse, ParseResult

from vkbottle import ABCRule
from vkbottle.bot import Message

def list_startswith(list1: list[str], list2: list[str]):
    for part1, part2 in zip(list1, list2):
        if part1 != part2:
            return False
    return True


def parse_url(text: str) -> Optional[ParseResult]:
    try:
        url = urlparse(text)
        return url
    except ValueError:
        return None

class UrlRule(ABCRule[Message]):

    def __init__(self, *allowed_domains):
        self.allowed_domains = [domain.split(".")[::-1] for domain in allowed_domains]

    async def check(self, event: Message) -> Union[dict, bool]:
        url = parse_url(event.text)
        if not url:
            return False
        netloc = url.netloc.split(":")[0] # Strip port. i have no clue why you ever need that.
        netloc = netloc.split(".")[::-1]
        for domain in self.allowed_domains:
            if list_startswith(netloc, domain):
                return {"url": url}
        return False