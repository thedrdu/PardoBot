#Might paywall this because it could cost money to run on API

import functools
import disnake
import time
import os, io, aiohttp, asyncio, itertools
from async_timeout import timeout
from disnake.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import youtube_dl, ffmpeg
FFMPEG_OPTIONS = {'before_options' : '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options' : '-vn'}
YDL_OPTIONS = {'format' : 'bestaudio'}

class MusicCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.voice_check.start()
    
    @tasks.loop(seconds=1.0)
    async def voice_check(self):
        '''PardoBot will automatically leave the Voice Channel if inactive for one minute.'''
        for client in self.bot.voice_clients:
            if not client.is_playing():
                for x in range(60):
                    await asyncio.sleep(1)
                    if client.is_playing():
                        return
                await client.disconnect()
    
    @commands.slash_command(
        name="play",
        description="Plays a YouTube link in the user's Voice Channel."
    )
    async def play(self, inter: disnake.ApplicationCommandInteraction, url: str):
        if inter.author.voice is None:
            await inter.response.send_message(content=f"Join a voice channel first!", ephemeral=True)
            return
        await inter.response.defer()

        channel = inter.author.voice.channel
        voice_client = disnake.utils.get(self.bot.voice_clients, guild=inter.guild)
        if voice_client is None:
            voice_client = await channel.connect()
        voice_client.stop()
        await inter.edit_original_message(content=f"Downloading song...")
        
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            info = ydl.extract_info(url, download=False)
            source_url = info['formats'][0]['url']
            source = await disnake.FFmpegOpusAudio.from_probe(source_url,**FFMPEG_OPTIONS)
        
        voice_client.play(source)
        
        await inter.edit_original_message(content=f"Now playing in {inter.author.voice.channel.mention}: {url}")
        
    @commands.slash_command(
        name="disconnect",
        description="Disconnects from the Voice Channel"
    )
    async def disconnect(self, inter: disnake.ApplicationCommandInteraction):
        voice_client = disnake.utils.get(self.bot.voice_clients, guild=inter.guild)
        await voice_client.disconnect()
        await inter.response.send_message(content=f"PardoBot successfully disconnected from {inter.author.voice.channel.mention}!")
    
def setup(bot: commands.Bot):
    bot.add_cog(MusicCommand(bot))