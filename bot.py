import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

class SkinWalker(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print(f'Logged on as {self.user}!')

    async def on_voice_state_update(self, member, before, after):
        try:
            print(f"User {member} triggered a voice event on the {after.channel} channel")
            user_count = len(after.channel.members)
            if user_count >= 2:
                try:
                    await after.channel.connect()  # Join the voice channel
                    print(f"Joined voice channel: {after.channel.name}")
                except discord.errors.ClientException as e:
                    print(f"Error joining voice channel: {e}")
        except AttributeError:
            print("No channel found, user left the chat")

if __name__ == "__main__":
    load_dotenv()
    token = os.environ.get("DISCORD_TOKEN")
    intents = discord.Intents.default()
    intents.message_content = True

    client = SkinWalker(intents=intents)
    client.run(token)
