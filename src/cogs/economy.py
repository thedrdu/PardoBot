import disnake
from disnake.ext import commands
import random
import collections
import sqlite3
import os
from dotenv import load_dotenv
from data.economy_util import update_balance, get_balance
DB_PATH = os.getenv('DB_PATH')

def custom_cooldown(message):
    return commands.Cooldown(1, 10)  # 1 per 10 secs

class EconomyCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.slash_command(
        name="bal",
        description="Returns user balance.",
    )
    # @commands.dynamic_cooldown(custom_cooldown, commands.BucketType.user)
    async def bal(self, inter: disnake.ApplicationCommandInteraction):
        bal = get_balance(inter.author.id)
        # embed = disnake.Embed(description=)
        await inter.response.send_message(content=f"Balance: {bal}")
       
def setup(bot: commands.Bot):
    bot.add_cog(EconomyCommand(bot))