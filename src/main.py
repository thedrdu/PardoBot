# author: thedrdu

import disnake
from disnake.ext import commands
import os
import asyncio
import math
import random
from datetime import datetime
from disnake.ext.commands import guild_only

from dotenv import load_dotenv
from isort import file, stream
load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

intents = disnake.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
intents.emojis = True
intents.emojis_and_stickers = True

bot = commands.Bot(
    sync_commands_debug=False,
    intents=intents,
)

@bot.event
async def online():
    channel = bot.get_channel(992809780143988808) #hard-coded
    current_time = datetime.now().strftime("%H:%M:%S")
    await channel.send(f"PardoBot is online! [Time: {current_time}]")

@bot.event
async def on_ready():
    print("***** [ PardoBot is now online! ] *****")
    game = disnake.Game("Honkai Impact 3rd")
    await online()
    await bot.change_presence(status=disnake.Status.streaming, activity=game)
    
bot.load_extension("cogs.util")
bot.load_extension("cogs.genshin")
# bot.load_extension("cogs.moderation")
bot.load_extension("cogs.blackjack")
bot.load_extension("cogs.economy")
bot.load_extension("cogs.roulette")
bot.load_extension("cogs.rps")

'''Passive Commands'''
@bot.listen()
async def on_message(message: disnake.Message):
    if message.author.bot:
        return
    if message.content.lower() == "nya":
        await message.author.send("Nya!")

'''Slash Commands'''

@bot.slash_command(
    name="pardopog",
    description="Returns PardoPOG."
)
async def pardopog(inter: disnake.ApplicationCommandInteraction):
    f = disnake.File("./PardoPOG.png") #NOTE: This is a local file
    await inter.send(embed=disnake.Embed().set_image(file=f))
    
@bot.slash_command(
    name="hug",
    description="Hugs a user.",
    guild_only=True,
)
async def hug(inter: disnake.ApplicationCommandInteraction, user: disnake.User):
    f = disnake.File("./hug.gif") #NOTE: This is a local file
    embed = disnake.Embed(
        title=f"{inter.author.name} hugs {user.name}!",
        colour=0xF0C43F,
    )
    await inter.send(embed=embed.set_image(file=f), allowed_mentions=disnake.AllowedMentions.none())

bot.run(TOKEN)