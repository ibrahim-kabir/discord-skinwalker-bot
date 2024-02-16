import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
from service import RecordingService
import json
import random
from discord import FFmpegPCMAudio

class SkinWalker(commands.Bot):
    def __init__(self, recording_service: RecordingService, sentences_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recording_service = recording_service
        self.sentences_path = sentences_path
        self.load_settings()
        self.add_commands()

    def add_commands(self):
        @self.command(name="status", pass_context=True)
        async def status(ctx):
            print(ctx)
            await ctx.channel.send("Up and running!")
        
        @self.command(name="set_appearance_frequency", pass_context=True)
        async def set_appearance_frequency(ctx, frequency: int):
            self.appearance_frequency = frequency
            await ctx.send(f'Appearance frequency has been set to {frequency}')

        @self.command(name="set_min_user", pass_context=True)
        async def set_min_user(ctx, user: int):
            self.min_users = user
            await ctx.send(f'Minimum users have been set to {user}')

        @self.command(name="get_settings", pass_context=True)
        async def get_settings(ctx):
            await ctx.channel.send(f'Appearance frequency: {self.appearance_frequency}, Minimum users: {self.min_users}')

        @self.command(name="leave", help="Makes the bot leave the voice channel.", pass_context=True)
        async def leave(ctx):
            if ctx.voice_client is not None:
                await ctx.voice_client.disconnect()
            else:
                await ctx.send("I'm not connected to a voice channel.")   
        
    def load_settings(self):
        with open('settings.json', 'r') as file:
            settings = json.load(file)
        self.appearance_frequency = settings.get('appearance_frequency')
        self.min_users = settings.get('min_users')

    async def on_ready(self):
        print('Bot is ready!')
        self.join_channel_randomly.start()

    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            if after.channel is not None and len(after.channel.members) >= 2:
                self.recording_service.start_recording(after.channel)
            elif before.channel is not None and len(before.channel.members) < 2:
                self.recording_service.stop_recording()

    @tasks.loop(minutes=1)
    async def join_channel_randomly(self):
        if self.recording_service.is_recording and random.random() < (100 / self.appearance_frequency):
            channel = self.recording_service.channel
            await self.play_random_mp3(channel)

    async def play_random_mp3(self, channel):
        mp3_files = [f for f in os.listdir(self.sentences_path) if f.endswith('.mp3')]
        mp3_file = random.choice(mp3_files)
        print(mp3_file)
        connection = await channel.connect()
        print(os.path.isdir(self.sentences_path + mp3_file), self.sentences_path + mp3_file)
        connection.play(FFmpegPCMAudio(self.sentences_path + mp3_file))
        await self.disconnect()

if __name__ == "__main__":
    load_dotenv()
    skinwalker_token = os.environ.get("SKINWALKER_TOKEN")
    recording_service_token = os.environ.get("RECORDING_SERVICE_TOKEN")
    sentences_path = os.environ.get("SENTENCES_DIRECTORY_PATH")

    intents = discord.Intents.default()
    intents.message_content = True
    
    recording_service = RecordingService()
    recording_service.run(recording_service_token)

    skinwalker_client = SkinWalker(recording_service, sentences_path, command_prefix='/', intents=intents, self_bot=False)
    skinwalker_client.run(skinwalker_token)


