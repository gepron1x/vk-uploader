import os

import dotenv
dotenv.load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
USER_TOKEN = os.getenv("USER_TOKEN")

PLAYLIST_OWNER_ID = int(os.getenv("PLAYLIST_OWNER_ID", "-227509439"))