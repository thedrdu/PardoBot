import disnake
from disnake.ext import commands
import random
import collections


balances = {} # player id : balance

def custom_cooldown(message):
    return commands.Cooldown(1, 10)  # 1 per 10 secs

class BlackjackCommand(commands.Cog):
    # Note that we're using self as the first argument, since the command function is inside a class.
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    
    @commands.slash_command(
        name="bal",
        description="Checks user balance.",
    )
    async def bal(self, inter: disnake.ApplicationCommandInteraction):
        global balances
        if inter.author.id not in balances.keys():
            balances[inter.author.id] = 100
        await inter.send(content=balances[inter.author.id], ephemeral=True)
    
    
    @commands.slash_command(
        name="work",
        description="Earn 100 currency.",
    )
    @commands.dynamic_cooldown(custom_cooldown, commands.BucketType.user)
    async def work(self, inter: disnake.ApplicationCommandInteraction):
        global balances
        if inter.author.id not in balances.keys():
            balances[inter.author.id] = 100
        balances[inter.author.id] += 100
        await inter.response.send_message(embed=disnake.Embed(description=f"You earned 100 currency!"),ephemeral=True)
    
def setup(bot: commands.Bot):
    bot.add_cog(BlackjackCommand(bot))