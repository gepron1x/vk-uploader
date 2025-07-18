import sys
from os import getenv

from loguru import logger
from vkbottle import Bot, User

import config
import soundcloud
import youtube

logger.remove()
logger.add(sys.stderr, level="INFO")

bot = Bot(config.BOT_TOKEN)

bot.on.load(youtube.labeler)
bot.on.load(soundcloud.labeler)

bot.run_forever()
