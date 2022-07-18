import disnake
from disnake.ext import commands
import random
import collections
import sqlite3
import os
import asyncio
from dotenv import load_dotenv
from data.economy_util import update_balance, get_balance
DB_PATH = os.getenv('DB_PATH')

def get_highest_game_id(table: str):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    rows = cur.execute(f'''SELECT MAX(GAME_ID) FROM {table};''')
    max_game_id = rows.fetchone()[0]
    con.commit()
    con.close()
    return max_game_id

def insert_rps(insert_game_id: int, insert_user_id: int, choice: str = ""):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    rows = cur.execute(f'''SELECT USER_ID FROM rps WHERE GAME_ID={insert_game_id} AND USER_ID={insert_user_id}''')
    if rows.fetchone() is None:
        cur.execute(f'''INSERT INTO rps (GAME_ID,USER_ID,CHOICE) 
                    VALUES ({insert_game_id},{insert_user_id},"{choice}");''')
    else:
        cur.execute(f'''UPDATE rps SET CHOICE="{choice}" WHERE USER_ID={insert_user_id};''')
    con.commit()
    con.close()

def get_rps_participants(game_id):
    participants = []
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    rows = cur.execute(f'''SELECT USER_ID FROM rps WHERE GAME_ID={game_id} AND CHOICE!="";''')
    for user in rows:
        participants.append(user[0])
    con.commit()
    con.close()
    return participants

def rps(game_id):
    '''Returns winner's user_id'''
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    rows = cur.execute(f'''SELECT USER_ID,CHOICE FROM rps WHERE GAME_ID={game_id}''')
    user1 = rows.fetchone()
    user2 = rows.fetchone()
    if user1[1] == user2[1]:
        return 0, 0
    elif user1[1] == "rock":
        if user2[1] == "paper":
            return user2[0], user1[0]
        else:
            return user1[0], user2[0]
    elif user1[1] == "paper":
        if user2[1] == "scissors":
            return user2[0], user1[0]
        else:
            return user1[0], user2[0]
    elif user1[1] == "scissors":
        if user2[1] == "rock":
            return user2[0], user1[0]
        else:
            return user1[0], user2[0]
    return 0, 0

def get_final_embed(original_author: disnake.Member, target_user: disnake.Member, winner: disnake.Member, bet: int):
    embed = disnake.Embed(
        title=f"Rock Paper Scissors!",
        description=f"{original_author.mention} has challenged {target_user.mention}!\nBet: <:HonkaiCoin:997742624477818921> ~~**{bet}**~~"
        )
    embed.add_field(
        name=f"Participants",
        value=f"{original_author.mention}\n{target_user.mention}"
    )
    embed.add_field(
        name=f"Winner",
        value=f"{winner.mention} (+**<:HonkaiCoin:997742624477818921>{bet}**)"
    )
    embed.set_author(name=original_author, icon_url=original_author.display_avatar.url)
    return embed

def get_final_comps(user_id: int):
    final_comps = [
        disnake.ui.Button(label="Join", style=disnake.ButtonStyle.blurple, disabled=True),
        disnake.ui.Button(label="Start", style=disnake.ButtonStyle.green, disabled=True),
        disnake.ui.Button(label="Rules", style=disnake.ButtonStyle.gray, disabled=True),
        disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{user_id}~rpsquit"),
    ]
    return final_comps

class RPSCommand(commands.Cog):
    # Note that we're using self as the first argument, since the command function is inside a class.
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    @commands.slash_command(
        name="rps",
        description="Starts a rock paper scissors game.",
        guild_only=True,
    )
    async def rps(self, inter: disnake.ApplicationCommandInteraction, target_user: disnake.Member, bet: int):
        if target_user.id == inter.author.id:
            await inter.response.send_message(f"Cannot play yourself!", ephemeral=True)
            return
        player_balance = get_balance(inter.author.id)
        target_balance = get_balance(target_user.id)
        if bet > player_balance:
            await inter.response.send_message(f"Insufficient balance!", ephemeral=True)
            return
        elif bet > target_balance:
            await inter.response.send_message(f"Target has insufficient balance!", ephemeral=True)
        if bet < 0:
            await inter.response.send_message(f"Enter a non-negative number!", ephemeral=True)
            return
        
        embed = disnake.Embed(
            title=f"Rock Paper Scissors!",
            description=f"{inter.author.mention} has challenged {target_user.mention}!\nBet: <:HonkaiCoin:997742624477818921> **{bet}**"
            )
        embed.add_field(
            name=f"Participants",
            value=f"{inter.author.mention}\n{target_user.mention}"
        )
        embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
        
        game_id = get_highest_game_id("rps")
        if game_id is None: 
            game_id = 1
        else:
            game_id += 1
        insert_rps(game_id, inter.author.id)
        comps = [
            disnake.ui.Button(label="Rock", style=disnake.ButtonStyle.gray, custom_id=f"{game_id}~rpsrock~{inter.author.id}~{target_user.id}~{bet}"),
            disnake.ui.Button(label="Paper", style=disnake.ButtonStyle.blurple, custom_id=f"{game_id}~rpspaper~{inter.author.id}~{target_user.id}~{bet}"),
            disnake.ui.Button(label="Scissors", style=disnake.ButtonStyle.red, custom_id=f"{game_id}~rpsscissors~{inter.author.id}~{target_user.id}~{bet}"),
            disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~rpsquit"),
            ]
        await inter.response.send_message(embed=embed, components=comps)
    
    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        id_parts = inter.component.custom_id.split('~')
        button_id = id_parts[1]
        print(f"button_id: {button_id}")
        if button_id == "rpsrock":
            game_id = id_parts[0]
            original_author = await inter.bot.get_or_fetch_user(id_parts[2])
            target_user = await inter.bot.get_or_fetch_user(id_parts[3])
            if inter.author.id == int(id_parts[2]) or inter.author.id == int(id_parts[3]):
                bet = id_parts[4]
                insert_rps(game_id, inter.author.id, "rock")
                if len(get_rps_participants(game_id)) == 2:
                    results = rps(game_id)
                    winner_id = results[0]
                    loser_id = results[1]
                    if winner_id == 0:
                        embed = disnake.Embed(
                            title=f"Rock Paper Scissors!",
                            description=f"{original_author.mention} has challenged {target_user.mention}!\nBet: <:HonkaiCoin:997742624477818921> ~~**{bet}**~~"
                            )
                        embed.add_field(
                            name=f"Participants",
                            value=f"{original_author.mention}\n{target_user.mention}"
                        )
                        embed.add_field(
                            name=f"Winner",
                            value=f"**Tie!**"
                        )
                        embed.set_author(name=original_author, icon_url=original_author.display_avatar.url)
                        await inter.response.edit_message(embed=embed,components=get_final_comps(original_author.id))
                        return
                    
                    update_balance(winner_id, int(bet))
                    update_balance(loser_id, int(bet)*-1)
                    
                    winner = await inter.bot.get_or_fetch_user(winner_id)
                    await inter.response.edit_message(embed=get_final_embed(original_author, target_user, winner, bet),
                                                          components=get_final_comps(original_author.id))
                await inter.send(content=f"Response recorded!", ephemeral=True)
        if button_id == "rpspaper":
            game_id = id_parts[0]
            original_author = await inter.bot.get_or_fetch_user(id_parts[2])
            target_user = await inter.bot.get_or_fetch_user(id_parts[3])
            
            if inter.author.id == int(id_parts[2]) or inter.author.id == int(id_parts[3]):
                bet = id_parts[4]
                insert_rps(game_id, inter.author.id, "paper")
                if len(get_rps_participants(game_id)) == 2:
                    results = rps(game_id)
                    winner_id = results[0]
                    loser_id = results[1]
                    if winner_id == 0:
                        embed = disnake.Embed(
                            title=f"Rock Paper Scissors!",
                            description=f"{original_author.mention} has challenged {target_user.mention}!\nBet: <:HonkaiCoin:997742624477818921> ~~**{bet}**~~"
                            )
                        embed.add_field(
                            name=f"Participants",
                            value=f"{original_author.mention}\n{target_user.mention}"
                        )
                        embed.add_field(
                            name=f"Winner",
                            value=f"**Tie!**"
                        )
                        embed.set_author(name=original_author, icon_url=original_author.display_avatar.url)
                        await inter.response.edit_message(embed=embed,components=get_final_comps(original_author.id))
                        return
                    
                    update_balance(winner_id, int(bet))
                    update_balance(loser_id, int(bet)*-1)
                    
                    winner = await inter.bot.get_or_fetch_user(winner_id)
                    await inter.response.edit_message(embed=get_final_embed(original_author, target_user, winner, bet),
                                                          components=get_final_comps(original_author.id))
                await inter.send(content=f"Response recorded!", ephemeral=True)
        if button_id == "rpsscissors":
            game_id = id_parts[0]
            original_author = await inter.bot.get_or_fetch_user(id_parts[2])
            target_user = await inter.bot.get_or_fetch_user(id_parts[3])
            
            if inter.author.id == int(id_parts[2]) or inter.author.id == int(id_parts[3]):
                bet = id_parts[4]
                insert_rps(game_id, inter.author.id, "scissors")
                if len(get_rps_participants(game_id)) == 2:
                    results = rps(game_id)
                    winner_id = results[0]
                    loser_id = results[1]
                    if winner_id == 0:
                        embed = disnake.Embed(
                            title=f"Rock Paper Scissors!",
                            description=f"{original_author.mention} has challenged {target_user.mention}!\nBet: <:HonkaiCoin:997742624477818921> ~~**{bet}**~~"
                            )
                        embed.add_field(
                            name=f"Participants",
                            value=f"{original_author.mention}\n{target_user.mention}"
                        )
                        embed.add_field(
                            name=f"Winner",
                            value=f"**Tie!**"
                        )
                        embed.set_author(name=original_author, icon_url=original_author.display_avatar.url)
                        await inter.response.edit_message(embed=embed,components=get_final_comps(original_author.id))
                        return
                        
                    update_balance(winner_id, int(bet))
                    update_balance(loser_id, int(bet)*-1)
                    
                    winner = await inter.bot.get_or_fetch_user(winner_id)
                    await inter.response.edit_message(embed=get_final_embed(original_author, target_user, winner, bet),
                                                          components=get_final_comps(original_author.id))
                    await inter.response.edit_message(embed=embed,components=get_final_comps(original_author.id))
                await inter.send(content=f"Response recorded!", ephemeral=True)
        if button_id == "rpsquit":
            author_id = int(id_parts[0])
            if inter.author.id == author_id: #Verify author
                await inter.response.defer()
                await inter.delete_original_message()
                    
def setup(bot: commands.Bot):
    bot.add_cog(RPSCommand(bot))