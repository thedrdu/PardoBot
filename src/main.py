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
    #test_guilds=[123456789, 987654321]
)

@bot.event
async def online():
    channel = bot.get_channel(992809780143988808) #hard-coded
    current_time = datetime.now().strftime("%H:%M:%S")
    await channel.send(f"PardoBot is online! [Time: {current_time} EST]")

@bot.event
async def on_ready():
    print("***** [ PardoBot is now online! ] *****")
    game = disnake.Game("Honkai Impact 3rd")
    await online()
    await bot.change_presence(status=disnake.Status.streaming, activity=game)
    
bot.load_extension("cogs.say")  # Note: We did not append the .py extension.
bot.load_extension("cogs.util")  # Note: We did not append the .py extension.
bot.load_extension("cogs.button") # Note: We did not append the .py extension.
bot.load_extension("cogs.genshin")
bot.load_extension("cogs.moderation")
bot.load_extension("cogs.blackjack")
# bot.load_extension("cogs.economy")

'''Passive Commands'''
@bot.listen()
async def on_message(message: disnake.Message):
    if message.author.bot:
        return
    if message.content.lower() == "nya":
        # print("attempting to message")
        await message.author.send("Nya!")


'''Slash Commands'''

@bot.slash_command(
    name="diceroll",
    description="Returns a value between 1 and 6."
    # guild_ids=[1234, 5678]
)
async def diceroll(inter: disnake.ApplicationCommandInteraction):
    await inter.response.send_message(content=str(random.randint(1,6)))
    # await asyncio.sleep(2)


@bot.slash_command(
    name="pardopog",
    description="Returns PardoPOG."
    # guild_ids=[1234, 5678]
)
async def pardopog(inter: disnake.ApplicationCommandInteraction):
    f = disnake.File("./PardoPOG.png") #NOTE: This is a local file
    await inter.send(embed=disnake.Embed().set_image(file=f))
    
@bot.slash_command(
    name="hug",
    description="Hugs a user.",
    guild_only=True,
    # guild_ids=[1234, 5678]
)
async def hug(inter: disnake.ApplicationCommandInteraction, user: disnake.User):
    f = disnake.File("./hug.gif") #NOTE: This is a local file
    embed = disnake.Embed(
        title=f"{inter.author.name} hugs {user.name}!",
        colour=0xF0C43F,
    )
    await inter.send(embed=embed.set_image(file=f), allowed_mentions=disnake.AllowedMentions.none())

bot.run(TOKEN)