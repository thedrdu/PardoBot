import disnake
from disnake.ext import commands
import random
import collections
import sqlite3
import os
from datetime import datetime
from dotenv import load_dotenv
from data.economy_util import update_balance, get_balance, get_global_rank, get_server_rank, get_guild_leaderboard, get_global_leaderboard
DB_PATH = os.getenv('DB_PATH')

def custom_cooldown(message):
    return commands.Cooldown(1, 10)  # 1 per 10 secs

class EconomyCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.slash_command(
        name="leaderboard",
        description="Returns leaderboard of user balances.",
    )
    # @commands.dynamic_cooldown(custom_cooldown, commands.BucketType.user)
    async def leaderboard(self, inter: disnake.ApplicationCommandInteraction):
        comps = [
            disnake.ui.Button(label="Guild", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~guildleaderboard"), 
            disnake.ui.Button(label="Global", style=disnake.ButtonStyle.green, custom_id=f"{inter.author.id}~globalleaderboard"),
            disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~quitleaderboard"),
        ]
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S") 
        embed = get_guild_leaderboard(inter.guild)
        embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
        embed.set_footer(text=f"Data retrieved in {round(inter.bot.latency * 1000)}ms at {current_time}")
        await inter.response.send_message(embed=embed,components=comps,allowed_mentions=disnake.AllowedMentions.none())   
        
        
    @commands.slash_command(
        name="bal",
        description="Returns user balance.",
    )
    # @commands.dynamic_cooldown(custom_cooldown, commands.BucketType.user)
    async def bal(self, inter: disnake.ApplicationCommandInteraction, user: disnake.Member = None):
        if user is None:
            user = inter.author
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        bal = get_balance(user.id)
        global_rank = get_global_rank(user.id)
        server_rank = get_server_rank(user.id, inter.guild)
        embed = disnake.Embed(description=f"Global Rank: #**{global_rank}**\nServer Rank: #**{server_rank}**")
        embed.add_field(name=f"Balance",value=f"{bal}")
        embed.set_author(name=user, icon_url=user.display_avatar.url)
        embed.set_thumbnail(user.avatar)
        embed.set_footer(text=f"Data retrieved in {round(inter.bot.latency * 1000)}ms at {current_time}")
        await inter.response.send_message(embed=embed)
        
    @commands.slash_command(
        name="work",
        description="Increases user balance.",
    )
    @commands.dynamic_cooldown(custom_cooldown, commands.BucketType.user)
    async def work(self, inter: disnake.ApplicationCommandInteraction):
        work_amount = random.randint(200,400)
        update_balance(inter.author.id, work_amount)
        embed = disnake.Embed(description=f"Gained {work_amount}!")
        embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
        await inter.response.send_message(embed=embed, ephemeral=True)
    
    @work.error
    async def work_error(self, inter: disnake.ApplicationCommandInteraction, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = disnake.Embed(description=f"Too soon! Please wait {round(error.cooldown.get_retry_after())} seconds!")
            embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
            await inter.response.send_message(embed=embed, ephemeral=True)
    
    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        id_parts = inter.component.custom_id.split('~')
        button_id = id_parts[1]
        if button_id == "guildleaderboard":
            author_id = int(id_parts[0])
            if inter.author.id == author_id: #Verify author
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S") 
                embed = get_guild_leaderboard(inter.guild)
                embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
                embed.set_footer(text=f"Data retrieved in {round(inter.bot.latency * 1000)}ms at {current_time}")
                await inter.response.edit_message(embed=embed)
        if button_id == "globalleaderboard":
            author_id = int(id_parts[0])
            if inter.author.id == author_id: #Verify author
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S") 
                embed = get_global_leaderboard()
                embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
                embed.set_footer(text=f"Data retrieved in {round(inter.bot.latency * 1000)}ms at {current_time}")
                await inter.response.edit_message(embed=embed)
        if button_id == "quitleaderboard":
            author_id = int(id_parts[0])
            if inter.author.id == author_id: #Verify author
                await inter.response.defer()
                await inter.delete_original_message()
        
def setup(bot: commands.Bot):
    bot.add_cog(EconomyCommand(bot))