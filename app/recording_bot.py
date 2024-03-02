import os
import time
import interactions
from interactions import slash_command
from dotenv import load_dotenv
from pydub import AudioSegment, silence

voice_connections = {}
SAVE_DIRECTORY = "recording/"
load_dotenv()

class RecordingService(interactions.Client):
    def __init__(self):
        super().__init__()
        self.is_recording = False
        self.channel = None 
        print("Recording is ready")

    @slash_command(name="record", description="Joins a channel and starts recording")
    async def start_recording(self, ctx):
        print("start recording")
        self.channel = os.environ.get("CHANNEL_ID")
        
        if ctx.guild.id not in voice_connections:
            # Connect to the voice channel
            voice_channel = ctx.guild.get_channel(self.channel)
            if voice_channel:
                # Connect to the voice channel
                voice_state = await voice_channel.connect()
                voice_connections[ctx.guild_id] = voice_state
            else:
                await ctx.send("Already recording in this guild.")

        # Start recording
        await voice_connections[ctx.guild.id].start_recording()
        #await ctx.send("Starting recording!")
        self.is_recording = True
        
    

    @slash_command(name="stoprecord", description="Stops recording and disconnects")
    async def stop_recording(self, ctx):
        print("stop recording")
        if ctx.guild.id in voice_connections:
            # Stop recording
            await voice_connections[ctx.guild.id].stop_recording()
            self.is_recording = False
            #await ctx.send(files=[interactions.File(file, file_name=f"{user_id}.mp3") for user_id, file in voice_connections[ctx.guild.id].recorder.output.items()])
            print([interactions.File(file, file_name=f"{user_id}.mp3") for user_id, file in voice_connections[ctx.guild.id].recorder.output.items()])
            self.save_audio(ctx)
            # Disconnect from the voice channel
            await voice_connections[ctx.guild.id].disconnect()
            del voice_connections[ctx.guild.id]
            
            print("Recording stopped. I left the voice channel.")
            #await ctx.send("Stopped recording. Be ware of the Skinwalker...")
            self.make_sentences()

        else:
            await print("I'm not recording in this guild.")

    def save_audio(self, ctx):
        print("save audio")
        
        for user_id, audio_data in voice_connections[ctx.guild.id].recorder.output.items():
            file_name = f"{user_id}.mp3"
            file_path = os.path.join(SAVE_DIRECTORY, file_name)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, "wb") as file:
                file.write(audio_data.read())

    def make_sentences(self):
        print("Making sentences")

        # Process each audio file in the SAVE_DIRECTORY
        for file_name in os.listdir(SAVE_DIRECTORY):
            if file_name.endswith(".mp3") and not "_" in file_name:
                file_path = os.path.join(SAVE_DIRECTORY, file_name)
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
                    segment = audio[segment_start:segment_end]

                    # Check if the segment is less than 10 seconds or than 1.5 second
                    if len(segment) < 10000 or len(segment) < 1500:
                        segments.append(segment)

                # Save each segment as an audio file
                output_directory = os.path.join(SAVE_DIRECTORY)
                os.makedirs(output_directory, exist_ok=True)

                # Get current date and time with milliseconds
                current_time = time.strftime("%Y%m%d-%H%M%S-%f")
                for i, segment in enumerate(segments):
                    output_file = os.path.join(output_directory, f"{current_time}_{i}.mp3")
                    segment.export(output_file, format="mp3")
                    print(f"Saved {current_time}_{i}.mp3")
            
        self.delete_long_recordings()
        self.delete_old_sentences()
        print("Making sentences done")

    
    # Deletes all the mp3 files generated by the record bot.
    def delete_long_recordings(self):
        print("Deleting long recordings...")
        
        # Get a list of all files in the SAVE_DIRECTORY
        files = os.listdir(SAVE_DIRECTORY)

        # Iterate through the files
        for file_name in files:
            # Check if the file is an MP3 file and doesn't contain the word "Sentence" in its name
            if file_name.endswith(".mp3") and "_" not in file_name:
                # Delete the file
                os.remove(os.path.join(SAVE_DIRECTORY, file_name))
                print(f"Deleted {file_name}")

        # Print confirmation message
        print(f"Tous les fichiers créé par le bot RecordingService MP3 ont été supprimés du dossier '{SAVE_DIRECTORY}'.")

    # Deletes all sentences that are 1 hour old or more
    def delete_old_sentences(self):
        print("Deleting old recordings...")

        # Get the current time
        current_time = time.time()

        # Iterate through all files in the SAVE_DIRECTORY
        for filename in os.listdir(SAVE_DIRECTORY):
            filepath = os.path.join(SAVE_DIRECTORY, filename)
            if os.path.isfile(filepath) and filepath.endswith('.mp3'):
                # Get the modification time of the file
                file_modified_time = os.path.getmtime(filepath)
                # Check if the file is older than an hour
                if current_time - file_modified_time > 3600:  # 3600 seconds = 1 hour
                    # Delete the file
                    os.remove(filepath)
                    print(f"Deleted {filename}")

        print("Old recordings deletion completed.")

    


