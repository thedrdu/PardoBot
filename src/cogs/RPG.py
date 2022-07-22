from email.policy import default
import disnake
from disnake.ext import commands
import random
from datetime import datetime
import collections
import sqlite3
import os
from dotenv import load_dotenv
from data.RPG_util import get_stats, get_level, add_exp, progress_to_next, add_enemy, get_enemy_stats

'''
Attack increases damage by 1

Defense negates 1 point of incoming damage up to 90% of total incoming damage
(so for example if you get hit by a 10dmg attack with 10 def, you take 1dmg)

Dexterity is a requirement for equipping certain equipment. It also increases hit rate(+0.5% per dex)

LUCK increases crit rate
'''

_ENEMIES = {
    "Anemo Slime" : [1,1,0,0,3],
    
}

_ENEMY_ICONS = {
    "Anemo Slime" : "https://static.wikia.nocookie.net/gensin-impact/images/7/71/Enemy_Anemo_Slime_Icon.png/revision/latest?cb=20201125224426",
    
}

def default_comps(user_id: int):
    default_comps = [
        disnake.ui.Button(label="Adventure", style=disnake.ButtonStyle.green, custom_id=f"{user_id}~RPGadventure"),
        disnake.ui.Button(label="Equipment", style=disnake.ButtonStyle.blurple, custom_id=f"{user_id}~RPGequipment"),
        disnake.ui.Button(label="Inventory", style=disnake.ButtonStyle.blurple, custom_id=f"{user_id}~RPGinventory"),
        disnake.ui.Button(label="Stats", style=disnake.ButtonStyle.gray, custom_id=f"{user_id}~RPGstats"),
        disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{user_id}~RPGquit")
    ]
    return default_comps

async def start_fight_enemy(inter: disnake.ApplicationCommandInteraction):
    enemy = random.choice(list(_ENEMIES.keys()))
    enemy_id = add_enemy(enemy, _ENEMIES[enemy])
    stats = get_enemy_stats(enemy_id)
    battle_comps = [
        disnake.ui.Button(label="Fight", style=disnake.ButtonStyle.green, custom_id=f"{inter.author.id}~RPGfight~{enemy_id}"),
        disnake.ui.Button(label="Heal", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~RPGheal~{enemy_id}"),
        disnake.ui.Button(label="Run", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~RPGrun~{enemy_id}"),
        disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~RPGquit~{enemy_id}")
    ]
    embed = disnake.Embed(
        title=f"Battle vs. {enemy}",
        description="Press any button!"
    )
    embed.add_field(name=f"{enemy}'s HP",value=f"{stats[4]}")
    embed.set_thumbnail(_ENEMY_ICONS[enemy])
    embed.set_author(name=f"{inter.author}", icon_url=f"{inter.author.display_avatar.url}")
    await inter.response.edit_message(embed=embed, components=battle_comps)

class RPG(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    

    @commands.slash_command()
    async def rpg(self, inter: disnake.ApplicationCommandInteraction):
        """
        Brings up the main RPG panel: Adventure | Equipment | Inventory | Stats | Quit
        """
        embed = disnake.Embed(
            title="PardoBot RPG!",
            description="Press any button!"
        )
        embed.set_thumbnail(f"{inter.author.avatar}")
        embed.set_author(name=f"{inter.author}", icon_url=f"{inter.author.display_avatar.url}")
        await inter.response.send_message(embed=embed, components=default_comps(inter.author.id))
    
    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        id_parts = inter.component.custom_id.split('~')
        button_id = id_parts[1]
        
        if button_id == "RPGadventure":
            author_id = int(id_parts[0])
            if author_id == inter.author.id:
                await start_fight_enemy(inter)
                # gained_exp = random.randint(10,20)
                # add_exp(inter.author.id, gained_exp)
                # embed = disnake.Embed(
                #     title=f"{inter.author.name}'s Adventure!",
                #     description=f"Gained {gained_exp} EXP"
                # )
                # embed.set_thumbnail(f"{inter.author.avatar}")
                # embed.set_author(name=f"{inter.author}", icon_url=f"{inter.author.display_avatar.url}")
                # comps = [
                #     disnake.ui.Button(label="Adventure", style=disnake.ButtonStyle.green, custom_id=f"{inter.author.id}~RPGadventure"),
                #     disnake.ui.Button(label="Main Menu", style=disnake.ButtonStyle.green, custom_id=f"{inter.author.id}~RPGmainmenu"),
                #     disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~RPGquit")
                # ]
                # await inter.response.edit_message(embed=embed, components=comps)
        
        if button_id == "RPGmainmenu":
            author_id = int(id_parts[0])
            if author_id == inter.author.id:
                embed = disnake.Embed(
                    title="PardoBot RPG!",
                    description="Press any button!"
                )
                embed.set_thumbnail(f"{inter.author.avatar}")
                embed.set_author(name=f"{inter.author}", icon_url=f"{inter.author.display_avatar.url}")
                await inter.response.edit_message(embed=embed, components=default_comps(inter.author.id))
        
        if button_id == "RPGstats":
            author_id = int(id_parts[0])
            if author_id == inter.author.id:
                stats = get_stats(inter.author.id) #EXP,ATT,DEF,DEX,LUCK,COINS,HP
                embed = disnake.Embed(
                    title=f"{inter.author.name}'s Stats",
                    description=f"Level: {get_level(stats[0])} ({progress_to_next(stats[0])}% to next)\nEXP: {stats[0]}\nCoins: <:HonkaiCoin:997742624477818921>{stats[5]}"
                )
                embed.add_field(name=f"HP", value=f"{stats[6]}")
                embed.add_field(name=f"ATTACK", value=f"{stats[1]}")
                embed.add_field(name=f"DEFENSE", value=f"{stats[2]}")
                embed.add_field(name=f"DEXTERITY", value=f"{stats[3]}")
                embed.add_field(name=f"LUCK", value=f"{stats[4]}")
                embed.set_thumbnail(f"{inter.author.avatar}")
                embed.set_author(name=f"{inter.author}", icon_url=f"{inter.author.display_avatar.url}")
                comps = [
                    disnake.ui.Button(label="Main Menu", style=disnake.ButtonStyle.green, custom_id=f"{inter.author.id}~RPGmainmenu"),
                    disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~RPGquit")
                ]
                await inter.response.edit_message(embed=embed, components=comps)
                
        if button_id == "RPGquit": #Does not require game id
            author_id = int(id_parts[0])
            if inter.author.id == author_id: #Verify author
                await inter.response.defer()
                await inter.delete_original_message()
def setup(bot: commands.Bot):
    bot.add_cog(RPG(bot))