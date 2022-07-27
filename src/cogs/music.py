import disnake
import os, io, aiohttp, asyncio, itertools
from disnake.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import youtube_dl
import ffmpeg

class MusicCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.slash_command(
        name="play",
        description="Plays a YouTube link in the user's Voice Channel."
    )
    async def play(self, inter: disnake.ApplicationCommandInteraction, url: str):
        await inter.response.defer()
        if inter.author.voice is None:
            await inter.edit_original_message(content=f"Join a voice channel first!",ephemeral=True)
            return
        channel = inter.author.voice.channel
        voice_client = await channel.connect()
        voice_client.stop()
        FFMPEG_OPTIONS = {'before_options' : '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options' : '-vn'}
        YDL_OPTIONS = {'format' : 'bestaudio'}
        
        await inter.edit_original_message(content=f"Downloading song...")
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            source_url = info['formats'][0]['url']
            source = await disnake.FFmpegOpusAudio.from_probe(source_url,**FFMPEG_OPTIONS)
            voice_client.play(source)
        await inter.edit_original_message(content=f"Now playing in {inter.author.voice.channel.mention}: {url}")
            
    @commands.slash_command(
        name="disconnect",
        description="testing command"
    )
    async def disconnect(self, inter: disnake.ApplicationCommandInteraction):
        voice_client = disnake.utils.get(self.bot.voice_clients, guild=inter.guild)
        await voice_client.disconnect()
        await inter.response.send_message(content=f"PardoBot successfully disconnected from {inter.author.voice.channel.mention}!")
    
def setup(bot: commands.Bot):
    bot.add_cog(MusicCommand(bot))