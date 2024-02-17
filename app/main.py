import discord
from dotenv import load_dotenv
import os
from recording_bot import RecordingService
from skinwalker_bot import SkinWalker
import asyncio

load_dotenv()

skinwalker_token = os.environ.get("SKINWALKER_TOKEN")
recording_service_token = os.environ.get("RECORDING_SERVICE_TOKEN")
sentences_path = os.environ.get("RECORDING_DIRECTORY_PATH")
guild_id = os.environ.get("GUILD_ID")
intents = discord.Intents.default()
intents.message_content = True



if __name__ == "__main__":
    recording_service = RecordingService()
    skinwalker_service = SkinWalker(guild_id, recording_service, sentences_path, intents=intents)

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(recording_service.start(recording_service_token))
    loop.create_task(skinwalker_service.run(skinwalker_token))
    loop.run_forever()
    print("Bots have stopped.")
