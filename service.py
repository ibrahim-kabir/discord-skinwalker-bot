import os
import interactions
from interactions import slash_command
from interactions import Client, Intents
from dotenv import load_dotenv


voice_connections = {}

SAVE_DIRECTORY = "recordings/"

bot = Client(intents=Intents.DEFAULT)

@slash_command(name="record", description="Joins a channel and starts recording")
async def start_record(ctx):
    if ctx.guild.id not in voice_connections:
        # Connect to the voice channel
        voice_state = await ctx.author.voice.channel.connect()
        voice_connections[ctx.guild.id] = voice_state
    else:
        await ctx.send("Already recording in this guild.")

    # Start recording
    await voice_connections[ctx.guild.id].start_recording()
    #await asyncio.sleep(5)
    

@slash_command(name="stoprecord", description="Stops recording and disconnects")
async def stop_record(ctx):
    if ctx.guild.id in voice_connections:
        # Stop recording
        await voice_connections[ctx.guild.id].stop_recording()
        #await ctx.send(files=[interactions.File(file, file_name=f"{user_id}.mp3") for user_id, file in voice_connections[ctx.guild.id].recorder.output.items()])
        print([interactions.File(file, file_name=f"{user_id}.mp3") for user_id, file in voice_connections[ctx.guild.id].recorder.output.items()])
        
        for user_id, audio_data in voice_connections[ctx.guild.id].recorder.output.items():
            file_name = f"{user_id}.mp3"
            file_path = os.path.join(SAVE_DIRECTORY, file_name)
            with open(file_path, "wb") as file:
                file.write(audio_data.read())
        # Disconnect from the voice channel
        await voice_connections[ctx.guild.id].disconnect()
        del voice_connections[ctx.guild.id]
        
        await ctx.send("Recording stopped. I left the voice channel.")

    else:
        await ctx.send("I'm not recording in this guild.")

if __name__ == "__main__":
    token = os.environ.get("RECORDING_SERVICE_TOKEN")
    bot.start(token)