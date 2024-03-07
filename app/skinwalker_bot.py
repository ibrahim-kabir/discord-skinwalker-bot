import os
from recording_bot import RecordingService
import json
import random
import interactions
from interactions import slash_command, Task, IntervalTrigger
from interactions.api.voice.audio import AudioVolume
from interactions.api.events import VoiceStateUpdate
from interactions import listen
import asyncio
from pydub import AudioSegment

class SkinWalker(interactions.Client):
    def __init__(self, recording_service: RecordingService, recording_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recording_service = recording_service
        self.recording_path = recording_path
        self.enable_state = True
        self.load_settings()

    @slash_command(name="status",description="Check if the bot is up and running.")
    async def status(self, ctx):
        await ctx.send("Up and running!")
        
    @slash_command(name="set_appearance_frequency", description="Set the frequency with which the bot makes appearances in voice channels.")
    async def set_appearance_frequency(self, ctx, frequency: int):
        self.appearance_frequency = frequency
        await ctx.send(f'Appearance frequency has been set to {frequency}')

    @slash_command(name="set_min_user", description="Set the minimum number of users required in a voice channel for the bot to join.")
    async def set_min_user(self, ctx, user: int):
        self.min_users = user
        await ctx.send(f'Minimum users have been set to {user}')

    @slash_command(name="get_settings", description="View the current settings for the bot.")
    async def get_settings(self, ctx):
        await ctx.send(f'Appearance frequency: {self.appearance_frequency}, Minimum users: {self.min_users}')
    
    @slash_command(name="enable", description="enable the bot.")
    async def enable_command(self, ctx):
        self.enable()
        await ctx.send('The Skinwalker bot has been enabled.')

    @slash_command(name="disable", description="disable the bot.")
    async def disable_command(self, ctx):
        self.disable()
        await ctx.send('The Skinwalker bot has been disabled.')   

    @listen(VoiceStateUpdate)
    async def on_voice_state_update(self, event):
        if event.after and event.before and event.after.channel != event.before.channel:
            if event.after.channel is not None and len(event.after.channel.members) >= self.min_users and self.enable:
                self.recording_service.start_recording(event.after.channel)
                try:
                    self.join_channel_randomly.start()
                except RuntimeError:
                    pass
            elif event.before.channel is not None and len(event.before.channel.members) < self.min_users:
                self.disable()

    def enable(self):
        self.enable_state = True
        
    def disable(self):
        self.enable_state = False
        self.recording_service.stop_recording()
        self.join_channel_randomly.stop()

    def load_settings(self):
        with open('settings.json', 'r') as file:
            settings = json.load(file)
        self.appearance_frequency = settings.get('appearance_frequency')
        self.min_users = settings.get('min_users')

    @Task.create(IntervalTrigger(minutes=1))
    async def join_channel_randomly(self):
        print("I'm trying to join a channel !")
        if self.recording_service.is_recording and random.random() < (100 / self.appearance_frequency):
            channel = self.recording_service.channel
            await self.play_random_mp3(channel)

    async def play_random_mp3(self, channel):
        mp3_files = [f for f in os.listdir(self.recording_path) if f.endswith('.mp3')]
        mp3_file = random.choice(mp3_files)
        mp3_path = self.recording_path + mp3_file
        audio = AudioVolume(mp3_path)
        audio_duration = len(AudioSegment.from_mp3(mp3_path)) / 1000  # duration in seconds
        
        voice_client = await channel.connect()
        await voice_client.play(audio)
        await asyncio.sleep(audio_duration)
        await voice_client.disconnect()