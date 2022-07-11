import disnake
from disnake.ext import commands

tally_count = 0
def increment_tally_count(amount):
    global tally_count
    tally_count += amount
    if tally_count > 999999999999:
        tally_count = 999999999999

def reset_tally_count():
    global tally_count
    tally_count = 0
        
class ButtonCommand(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.slash_command()
    async def button(self, inter: disnake.ApplicationCommandInteraction):
        """
        Sends a button.
        """
        comps = [
            disnake.ui.Button(label="test", style=disnake.ButtonStyle.blurple, custom_id="test")
        ]
        await inter.response.send_message(components=comps)


    @commands.slash_command()
    async def tally(self, inter: disnake.ApplicationCommandInteraction):
        """
        Sends a counter with buttons.
        """
        comps = [
            disnake.ui.Button(label="+1", style=disnake.ButtonStyle.green, custom_id="plusone"),
            disnake.ui.Button(label="+5", style=disnake.ButtonStyle.green, custom_id="plusfive"),
            disnake.ui.Button(label="x2", style=disnake.ButtonStyle.green, custom_id="timestwo"),
            disnake.ui.Button(label="Reset", style=disnake.ButtonStyle.red, custom_id="reset"),
            disnake.ui.Button(label="Exit", style=disnake.ButtonStyle.blurple, custom_id="exitTally")
        ]
        reset_tally_count()
        await inter.response.send_message(components=comps, content=f"{tally_count}")
    
    
    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        if inter.component.custom_id == "test":
            await inter.response.defer(ephemeral=True)
            comps = disnake.ui.ActionRow.rows_from_message(inter.message)
            comps[0].add_button(label="test2", style=disnake.ButtonStyle.green, custom_id="test2")
            await inter.edit_original_message(components=comps)
        if inter.component.custom_id == "plusone":
            await inter.response.defer(ephemeral=True)
            increment_tally_count(1)
            await inter.edit_original_message(content=f"{tally_count}   Last pressed by: {inter.author}")
        if inter.component.custom_id == "plusfive":
            await inter.response.defer(ephemeral=True)
            increment_tally_count(5)
            await inter.edit_original_message(content=f"{tally_count}   Last pressed by: {inter.author}")
        if inter.component.custom_id == "timestwo":
            await inter.response.defer(ephemeral=True)
            increment_tally_count(tally_count)
            await inter.edit_original_message(content=f"{tally_count}   Last pressed by: {inter.author}")
        if inter.component.custom_id == "reset":
            await inter.response.defer(ephemeral=True)
            reset_tally_count()
            await inter.edit_original_message(content=f"{tally_count}   Last pressed by: {inter.author}")
        if inter.component.custom_id == "exitTally":
            await inter.response.defer(ephemeral=True)
            reset_tally_count()
            await inter.delete_original_message()
            

def setup(bot: commands.Bot):
    bot.add_cog(ButtonCommand(bot))