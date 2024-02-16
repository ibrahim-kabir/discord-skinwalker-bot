import discord
from discord.ext import commands
from service import RecordingService
from dotenv import load_dotenv
import os

class SkinWalker(discord.Client):
    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_message(self, message):
        print(f'Message from {message.author}: {message.content}')

if __name__ == "__main__":
    load_dotenv()
    token = os.environ.get("DISCORD_TOKEN")
    intents = discord.Intents.default()
    intents.message_content = True

    client = SkinWalker(intents=intents)
    client.run()
