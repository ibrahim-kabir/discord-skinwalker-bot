from discord.ext import tasks
import os
from recording_bot import RecordingService
import json
import random
from discord import FFmpegPCMAudio
import discord
from discord import app_commands

class SkinWalker(discord.Client):
    def __init__(self, guild_id, recording_service: RecordingService, recording_path: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.recording_service = recording_service
        self.recording_path = recording_path
        self.guide_id = guild_id
        self.tree = app_commands.CommandTree(self)
        self.load_settings()
        
        @self.tree.command(name="status",description="Check if the bot is up and running.", guild=discord.Object(id=self.guide_id))
        async def status(interaction):
            await interaction.response.send_message("Up and running!")

        @self.tree.command(name="set_appearance_frequency", description="Set the frequency with which the bot makes appearances in voice channels.", guild=discord.Object(id=self.guide_id))
        async def set_appearance_frequency(interaction, frequency: int):
            self.appearance_frequency = frequency
            await interaction.response.send_message(f'Appearance frequency has been set to {frequency}')

        @self.tree.command(name="set_min_user", description="Set the minimum number of users required in a voice channel for the bot to join.", guild=discord.Object(id=self.guide_id))
        async def set_min_user(interaction, user: int):
            self.min_users = user
            await interaction.response.send_message(f'Minimum users have been set to {user}')

        @self.tree.command(name="get_settings", description="View the current settings for the bot.", guild=discord.Object(id=self.guide_id))
        async def get_settings(interaction):
            await interaction.response.send_message(f'Appearance frequency: {self.appearance_frequency}, Minimum users: {self.min_users}')

        @self.tree.command(name="leave", description="Disconnects the bot from the voice channel it's currently in.", guild=discord.Object(id=self.guide_id))
        async def leave(interaction):
            if len(interaction.client.voice_clients) > 0:
                print(interaction.client.voice_clients)    
                await interaction.client.voice_clients.disconnect()
            else:
                await interaction.response.send_message("I'm not connected to a voice channel.")   
        
    def load_settings(self):
        with open('settings.json', 'r') as file:
            settings = json.load(file)
        self.appearance_frequency = settings.get('appearance_frequency')
        self.min_users = settings.get('min_users')

    async def on_ready(self):
        print('Bot is ready!')
        await self.tree.sync(guild=discord.Object(self.guide_id))

    async def on_voice_state_update(self, member, before, after):
        if before.channel != after.channel:
            if after.channel is not None and len(after.channel.members) >= 2:
                self.recording_service.start_recording(after.channel)
                self.join_channel_randomly.start()
            elif before.channel is not None and len(before.channel.members) < 2:
                self.recording_service.stop_recording()
                self.join_channel_randomly.stop()

    @tasks.loop(minutes=1)
    async def join_channel_randomly(self):
        print("I'm trying to join a channel !")
        if self.recording_service.is_recording and random.random() < (100 / self.appearance_frequency):
            channel = self.recording_service.channel
            await self.play_random_mp3(channel)

    async def play_random_mp3(self, channel):
        mp3_files = [f for f in os.listdir(self.recording_path) if f.endswith('.mp3')]
        mp3_file = random.choice(mp3_files)
        print(mp3_file)
        connection = await channel.connect()
        print(os.path.isdir(self.recording_path + mp3_file), self.recording_path + mp3_file)
        connection.play(FFmpegPCMAudio(self.recording_path + mp3_file))
        await self.disconnect()