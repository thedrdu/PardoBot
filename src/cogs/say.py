import disnake
from disnake.ext import commands


class SayCommand(commands.Cog):
    # Note that we're using self as the first argument, since the command function is inside a class.
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.slash_command(
        name="say",
        description="Sends a user's message via PardoBot.",
        # guild_ids=[1234, 5678]
    )
    async def say(self, inter: disnake.ApplicationCommandInteraction, arg):
        await inter.response.defer()
        await inter.send(arg)
        
def setup(bot: commands.Bot):
    bot.add_cog(SayCommand(bot))