from os import getenv

from vkbottle import User, VideoUploader, AudioUploader

import config
from uploaders import BatchAudioUploader, AlbumCoverUploader

user = User(config.USER_TOKEN)

video_uploader = VideoUploader(user.api)

audio_uploader = AudioUploader(user.api)

batch_audio_uploader = BatchAudioUploader(audio_uploader)

album_cover_uploader = AlbumCoverUploader(user.api)