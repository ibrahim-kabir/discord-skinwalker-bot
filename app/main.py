import discord
from dotenv import load_dotenv
import os
from recording_bot import RecordingService
from skinwalker_bot import SkinWalker
import threading

load_dotenv()

skinwalker_token = os.environ.get("SKINWALKER_TOKEN")
recording_service_token = os.environ.get("RECORDING_SERVICE_TOKEN")
sentences_path = os.environ.get("RECORDING_DIRECTORY_PATH")
guild_id = os.environ.get("GUILD_ID")
intents = discord.Intents.default()
intents.message_content = True

def start_recording_service():
    recording_service.run(recording_service_token)
    
def start_skinwalker():
    skinwalker_client.run(skinwalker_token)

if __name__ == "__main__":
    recording_service = RecordingService()
    skinwalker_client = SkinWalker(guild_id, recording_service, sentences_path,  intents=intents)
    thread_recording = threading.Thread(target=start_recording_service)
    thread_skinwalker = threading.Thread(target=start_skinwalker)
    thread_recording.start()
    thread_skinwalker.start()
    print("Bots are ready!")




