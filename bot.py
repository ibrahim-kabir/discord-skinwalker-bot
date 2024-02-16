import discord
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os
from service import RecordingService
import json
import random
from discord import FFmpegPCMAudio

class SkinWalker(commands.Bot):
    def __init__(self, sentences_path,command_prefix, *args, **kwargs):
        super().__init__(command_prefix,*args, **kwargs)
        self.recording_service = RecordingService()
        self.load_settings()
        self.sentences_path = sentences_path

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
        await channel.disconnect()

    @commands.command(name="set_appearance_frequency")
    async def set_appearance_frequency(self, ctx, frequency: int):
        self.appearance_frequency = frequency
        await ctx.send(f'Appearance frequency has been set to {frequency}')

    @commands.command(name="set_min_user")
    async def set_min_user(self, ctx, user: int):
        self.min_users = user
        await ctx.send(f'Minimum users have been set to {user}')

    @commands.command(name="get_settings")
    async def get_settings(self, ctx):
        await ctx.send(f'Appearance frequency: {self.appearance_frequency}, Minimum users: {self.min_users}')

    @commands.command(help="Makes the bot leave the voice channel.")
    async def leave(self, ctx):
        print("leave")
        try:
            await ctx.voice_client.disconnect()
        except Exception as e:
            print(e)

if __name__ == "__main__":
    load_dotenv()
    token = os.environ.get("DISCORD_TOKEN")
    sentences_path = os.environ.get("SENTENCES_DIRECTORY_PATH")

    intents = discord.Intents.default()
    intents.message_content = True

    client = SkinWalker(sentences_path, command_prefix='/', intents=intents)
    client.run(token)


