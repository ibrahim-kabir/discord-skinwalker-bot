import os
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
        #self.channel = channel
        if ctx.guild.id not in voice_connections:
            # Connect to the voice channel
            voice_state = await ctx.author.voice.channel.connect()
            voice_connections[ctx.guild.id] = voice_state
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
        print("making sentences")

        # Charger le fichier audio
        for file_name in os.listdir(SAVE_DIRECTORY):
            if file_name.endswith(".mp3"):
                file_path = os.path.join(SAVE_DIRECTORY, file_name)
                audio = AudioSegment.from_mp3(file_path)

        self.delete_old_recordings()

        # Trouver les indices de début et de fin de chaque segment de silence
        #silence_ranges = silence.detect_silence(audio, min_silence_len=1000, silence_thresh=-35)
        audio_trimmed = audio.strip_silence()

        # Split the trimmed audio segment into sub-segments of 10 seconds or less
        max_segment_duration = 10 * 1000  # 10 seconds in milliseconds
        segments = []
        for i in range(0, len(audio_trimmed), max_segment_duration):
            segment = audio_trimmed[i:i + max_segment_duration]
            segments.append(segment)
        """
        # Diviser le fichier audio en segments de silence
        segments = []
        for start, end in silence_ranges:
            # Découper le segment de silence en sous-segments de 10 secondes ou moins
            segment = audio[start:end]
            max_segment_duration = 10 * 1000  # 10 secondes en millisecondes
            sub_segments = []
            for i in range(0, len(segment), max_segment_duration):
                sub_segment = segment[i:i+max_segment_duration]
                sub_segments.append(sub_segment)
            segments.extend(sub_segments)
        """
        # Sauvegarder chaque segment en tant que fichier audio
        output_directory = os.path.join(SAVE_DIRECTORY)
        os.makedirs(output_directory, exist_ok=True)
        for i, segment in enumerate(segments):
            output_file = os.path.join(output_directory, f"{i}.mp3")
            segment.export(output_file, format="mp3")
        print("making sentences done")
    
    def delete_old_recordings(self):
        print("delete old recordings")
        
        fichiers = os.listdir(SAVE_DIRECTORY)

        # Parcourir la liste des fichiers
        for fichier in fichiers:
            # Vérifier si le fichier est un fichier MP3
            if fichier.endswith(".mp3"):
                # Supprimer le fichier
                os.remove(os.path.join(SAVE_DIRECTORY, fichier))

        # Message de confirmation
        print(f"Tous les fichiers MP3 ont été supprimés du dossier '{SAVE_DIRECTORY}'.")


if __name__ == "__main__":
    bot = RecordingService()
    token = os.environ.get("RECORDING_SERVICE_TOKEN")
    
    bot.start(token)
    #bot.start_recording()
    


