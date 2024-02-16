from discord.ext import commands

class RecordingService(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_recording = False
        self.channel = None 
        print("Recording is ready")
        # ...

    def start_recording(self, channel):
        self.channel = channel 
        self.is_recording = True
        print("start recording")
        # ...

    def stop_recording(self):
        self.is_recording = False
        print("stop recording")
        # ...

    def save_audio(self, audio_data, filename):
        print("save audio")
        # ...

    def delete_old_recordings(self):
        print("delete old recordings")
        # ...
