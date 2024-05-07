import os
import json
import random
import time

from dotenv import load_dotenv

from interactions import slash_command, Task, IntervalTrigger, GuildVoice, OptionType, SlashContext, ChannelType, slash_option, Client
from interactions.api.voice.audio import AudioVolume
from pydub import AudioSegment, silence

class SkinWalker(Client):
    def __init__(self, recording_path: str,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load_settings()
        self.recording_path = recording_path
        self.ctx_recording = set()
        self.channel_option = None
        
    @slash_command(name="set_appearance_frequency", description="Set the frequency with which the bot makes appearances in voice channels.")
    @slash_option(
        name="frequency",
        description="Frequency of appearance in voice channels between 1% and 100%.",
        required=True,
        opt_type=OptionType.INTEGER,
        min_value = 1,
        max_value= 100)
    async def set_appearance_frequency(self, ctx: SlashContext, frequency: int):
        self.appearance_frequency = frequency
        self.update_settings(frequency)
        await ctx.send(f"Appearance frequency set to **{frequency}%**.")

    @slash_command(name="record", description="Joins a channel and starts recording")
    @slash_option(
        name="channel_option",
        description="Channel Option",
        required=True,
        opt_type=OptionType.CHANNEL,
        channel_types=[ChannelType.GUILD_VOICE])
    async def start_recording(self, ctx: SlashContext, channel_option: GuildVoice):
        self.channel_option = channel_option
        await ctx.send("Trying to connect..")
        await channel_option.connect()
        await ctx.voice_state.start_recording()
        await ctx.send(f"""**Connected and recording. 🎙️**
The bot will appear at a rate of **{self.appearance_frequency}%** each 30 seconds in this voice channel.
Use `/stop_recording` to stop recording and disconnect.""")
        self.ctx_recording.add(ctx)
        self.task_save_audio.start()
        self.play_random_task.start()

    @slash_command(name="stop_recording", description="Stops recording and disconnects")
    @slash_option(
        name="channel_option",
        description="Channel Option",
        required=True,
        opt_type=OptionType.CHANNEL,
        channel_types=[ChannelType.GUILD_VOICE])
    async def stop_recording(self, ctx: SlashContext, channel_option: GuildVoice):
            if channel_option is not None:
                await ctx.send("Trying to disconnect..")
                await ctx.voice_state.stop_recording()
                await channel_option.disconnect()
                await ctx.send("**Disconnected and stopped recording. **")
            else: 
                await ctx.send("I'm not recording in this discord server.")

    @slash_command(name="clean_audio", description="Deletes all audio files in the recording path")
    async def clean_audio(self, ctx: SlashContext):
            await ctx.send("Cleaning audio files.. 🧹")
            for file_name in os.listdir(self.recording_path):
                if file_name.endswith(".mp3"):
                    file_path = os.path.join(self.recording_path, file_name)
                    os.remove(file_path)
            await ctx.send("Audio files cleaned.")

    @Task.create(IntervalTrigger(seconds=30))
    async def play_random_task(self):
        if random.random() < (self.appearance_frequency / 100):
            await self.play_random_mp3(self.channel_option)

    async def play_random_mp3(self, channel: GuildVoice):
        try:
            if not os.path.exists(self.recording_path):
                os.makedirs(self.recording_path)
            mp3_files = [f for f in os.listdir(self.recording_path) if f.endswith('.mp3') and "_" in f]
            mp3_file = random.choice(mp3_files)
            mp3_path = self.recording_path + mp3_file
            audio = AudioVolume(mp3_path)
            
            if not channel.voice_state:
                await channel.connect()
            await channel.voice_state.play(audio)
        # No mp3 files
        except IndexError:
            return

    @Task.create(IntervalTrigger(minutes=1))
    async def task_save_audio(self):
        for ctx in self.ctx_recording:
            if not ctx.voice_state:
                await self.channel_option.connect()
            await ctx.voice_state.stop_recording()
            self.save_audio(ctx)
            self.split_audio_to_sentence()
            self.delete_long_recordings()
            self.delete_old_sentences()
            await ctx.voice_state.start_recording()

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

    def save_audio(self, ctx: SlashContext):
        """Save audio data for each user in the voice state recorder.
        """
        for user_id, audio_data in ctx.voice_state.recorder.output.items():
            file_name = f"{user_id}.mp3"
            file_path = os.path.join(self.recording_path, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as file:
                file.write(audio_data.read())

    def split_audio_to_sentence(self):
            """
            Split the audio files in the recording path into sentences based on silence detection.

            This method processes each audio file in the `recording_path` directory. It detects silence ranges in the audio
            and creates segments between the silences. Segments that are less than 10 seconds or less than 1.5 seconds are
            saved as separate audio files.

            Note: This method assumes that the audio files are in the MP3 format.
            """
            
            # Process each audio file in the self.recording_path
            for file_name in os.listdir(self.recording_path):
                if file_name.endswith(".mp3") and "_" not in file_name:
                    file_path = os.path.join(self.recording_path, file_name)
                    audio = AudioSegment.from_mp3(file_path)

                    # Detect silence ranges in the audio
                    silence_ranges = silence.detect_silence(audio, min_silence_len=1000, silence_thresh=-30)

                    # Create segments between silences
                    segments = []
                    for i, (start, end) in enumerate(silence_ranges):
                        # Calculate the end point for the segment (start of the next silence - 500 milliseconds)
                        if i < len(silence_ranges) - 1:
                            next_start = silence_ranges[i+1][0]
                            segment_end = min(next_start + 700, len(audio))
                        else:
                            # If it's the last silence, end the segment at the end of the audio
                            segment_end = len(audio)
                        
                        # Calculate the start point for the segment (end of the current silence - 500 milliseconds)
                        segment_start = max(end - 700, 0)
                        
                        # Create a segment from the calculated start point to the calculated end point
                        segment: AudioSegment = audio[segment_start:segment_end]

                        # Check if the segment is less than 10 seconds and superior than 1.5 second
                        
                        if len(segment) < 10000 and len(segment) > 1500:
                            segments.append(segment)

                    # Save each segment as an audio file
                    output_directory = os.path.join(self.recording_path)
                    os.makedirs(output_directory, exist_ok=True)

                    # Get current date and time with milliseconds
                    current_time = time.strftime("%Y%m%d-%H%M%S-%f")
                    for i, segment in enumerate(segments):
                        output_file = os.path.join(output_directory, f"{current_time}_{i}.mp3")
                        segment.export(output_file, format="mp3")
    
    def delete_long_recordings(self):
        """
        Deletes all long recordings in the specified recording path.

        This method iterates through all files in the recording path and deletes any MP3 files
        that do not contain the word "Sentence" in their name.
        """
        # Get a list of all files in the self.recording_path
        files = os.listdir(self.recording_path)

        # Iterate through the files
        for file_name in files:
            # Check if the file is an MP3 file and doesn't contain the word "Sentence" in its name
            if file_name.endswith(".mp3") and "_" not in file_name:
                # Delete the file
                os.remove(os.path.join(self.recording_path, file_name))

    def delete_old_sentences(self):
        """
        Deletes old recording files that are older than an hour.

        This method iterates through all files in the `self.recording_path` directory and checks if each file is older than an hour.
        If a file is older than an hour, it is deleted from the directory.
        """
        # Get the current time
        current_time = time.time()

        # Iterate through all files in the self.recording_path
        for filename in os.listdir(self.recording_path):
            filepath = os.path.join(self.recording_path, filename)
            if os.path.isfile(filepath) and filepath.endswith('.mp3'):
                # Get the modification time of the file
                file_modified_time = os.path.getmtime(filepath)
                # Check if the file is older than an hour
                if current_time - file_modified_time > 3600:  # 3600 seconds = 1 hour
                    # Delete the file
                    os.remove(filepath)

if __name__ == "__main__":
    load_dotenv()
    skinwalker_token = os.environ.get("SKINWALKER_TOKEN")
    recording_path = os.environ.get("RECORDING_DIRECTORY_PATH", "./recording/")
    skinwalker_client = SkinWalker(recording_path)
    skinwalker_client.start(skinwalker_token)