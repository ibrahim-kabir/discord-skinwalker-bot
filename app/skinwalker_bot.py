import os
import json
import random
import interactions
from interactions import slash_command, Task, IntervalTrigger
from interactions.api.voice.audio import AudioVolume
from interactions.api.events import VoiceStateUpdate
from interactions import listen
import asyncio
from pydub import AudioSegment
from dotenv import load_dotenv

class SkinWalker(interactions.Client):
    def __init__(self, recording_path: str, recording_service_id,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recording_service_id = int(recording_service_id)
        self.recording_path = recording_path
        self.load_settings()
        self.channels_recording = set()
        
    @slash_command(name="set_appearance_frequency", description="Set the frequency with which the bot makes appearances in voice channels.")
    async def set_appearance_frequency(self, ctx, frequency: int):
        self.appearance_frequency = frequency
        self.update_settings(frequency)
        

    @listen(VoiceStateUpdate)
    async def on_voice_state_update(self, event):
        if event.after:
            # Check if the recording service is in the channel        
            for member in event.after.channel.members: 
                if member.id == self.recording_service_id:
                    self.channels_recording.add(event.after.channel)
                    self.join_channel_randomly.start()
                    return
            if event.after.channel in self.channels_recording:
                self.channels_recording.remove(event.after.channel)

    def load_settings(self):
        with open('settings.json', 'r') as file:
            settings = json.load(file)
        self.appearance_frequency = settings.get('appearance_frequency')

    def update_settings(self, frequency):
        with open('settings.json', 'r') as file:
            settings = json.load(file)
        
        settings['appearance_frequency'] = frequency
        
        with open('settings.json', 'w') as file:
            json.dump(settings, file)

    @Task.create(IntervalTrigger(seconds=10))
    async def join_channel_randomly(self):
        if random.random() < (100 / self.appearance_frequency):
            for channel in self.channels_recording:
                await self.play_random_mp3(channel)
                raise ValueError(self.channels_recording)
        raise ValueError("10s has passed")

    async def play_random_mp3(self, channel):
        try:
            if not os.path.exists(self.recording_path):
                os.makedirs(self.recording_path)
            mp3_files = [f for f in os.listdir(self.recording_path) if f.endswith('.mp3')]
            mp3_file = random.choice(mp3_files)
            mp3_path = self.recording_path + mp3_file
            audio = AudioVolume(mp3_path)
            audio_duration = len(AudioSegment.from_mp3(mp3_path)) / 1000 + 1 # duration in seconds
            
            voice_client = await channel.connect()
            await voice_client.play(audio)
            await asyncio.sleep(audio_duration)
            await voice_client.disconnect()
        # No mp3 files
        except IndexError:
            return

if __name__ == "__main__":
    load_dotenv()
    skinwalker_token = os.environ.get("SKINWALKER_TOKEN")
    recording_path = os.environ.get("RECORDING_DIRECTORY_PATH")
    recording_service_id = os.environ.get("RECORDING_SERVICE_ID")
    skinwalker_client = SkinWalker(recording_path, recording_service_id)
    skinwalker_client.start(skinwalker_token)