import discord
from dotenv import load_dotenv
import os
from app.recording_bot import RecordingService
from app.skinwalker_bot import SkinWalker

load_dotenv()

skinwalker_token = os.environ.get("SKINWALKER_TOKEN")
recording_service_token = os.environ.get("RECORDING_SERVICE_TOKEN")
sentences_path = os.environ.get("SENTENCES_DIRECTORY_PATH")
intents = discord.Intents.default()
intents.message_content = True

recording_service = RecordingService(command_prefix='/',  intents=intents)
recording_service.run(recording_service_token)
skinwalker_client = SkinWalker(recording_service, sentences_path, command_prefix='/', intents=intents, self_bot=False)
skinwalker_client.run(skinwalker_token)


