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
    print(f"max_game_id: {max_game_id}")
    con.commit()
    con.close()
    return max_game_id

#NOTE: try using UNIQUE later
def insert_roulette(insert_game_id: int, insert_user_id: int):
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    rows = cur.execute(f'''SELECT USER_ID FROM roulette WHERE GAME_ID={insert_game_id} AND USER_ID={insert_user_id}''')
    if rows.fetchone() is None:
        cur.execute(f'''INSERT INTO roulette (GAME_ID,USER_ID) 
                    VALUES ({insert_game_id},{insert_user_id});''')
    con.commit()
    con.close()

def get_roulette_participants(game_id):
    participants = []
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    rows = cur.execute(f'''SELECT USER_ID FROM roulette WHERE GAME_ID={game_id};''')
    for user in rows:
        participants.append(user[0])
    con.commit()
    con.close()
    return participants


class RouletteCommand(commands.Cog):
    # Note that we're using self as the first argument, since the command function is inside a class.
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.slash_command(
        name="russianroulette",
        description="Starts a russian roulette session.",
        guild_only=True,
    )
    async def russianroulette(self, inter: disnake.ApplicationCommandInteraction, bet: int):
        player_balance = get_balance(inter.author.id)
        if bet > player_balance:
            await inter.response.send_message(f"Insufficient balance!", ephemeral=True)
            return
        if bet < 0:
            await inter.response.send_message(f"Enter a non-negative number!", ephemeral=True)
            return
        
        embed = disnake.Embed(title=f"Russian Roulette!",description=f"A russian roulette game has begun!\nBuy-in price: <:HonkaiCoin:997742624477818921> **{bet}**")
        embed.add_field(
            name=f"Participants",
            value=f"{inter.author.mention}\n"
        )
        embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
        
        game_id = get_highest_game_id("roulette")
        if game_id is None: 
            game_id = 1
        else:
            game_id += 1
        insert_roulette(game_id, inter.author.id)
        
        initial_comps = [
            disnake.ui.Button(label="Join", style=disnake.ButtonStyle.blurple, custom_id=f"{game_id}~roulettejoin~{inter.author.id}~{bet}"),
            disnake.ui.Button(label="Start", style=disnake.ButtonStyle.green, disabled=True, custom_id=f"{game_id}~roulettestart~{inter.author.id}~{bet}"),
            disnake.ui.Button(label="Rules", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~rouletterules"),
            disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~roulettequit"),
        ]
        await inter.response.send_message(embed=embed, components=initial_comps)
        #Game is now in default play state, game_id is guaranteed 
    
    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        id_parts = inter.component.custom_id.split('~')
        button_id = id_parts[1]

        if button_id == "roulettejoin": #Requires game id
            game_id = id_parts[0]
            author_id = id_parts[2]
            bet = id_parts[3]
            insert_roulette(game_id, inter.author.id)
            
            embed = disnake.Embed(title=f"Russian Roulette!",description=f"A russian roulette game has begun!\nBuy-in price: <:HonkaiCoin:997742624477818921> **{bet}**")
            participants = get_roulette_participants(game_id)
            value = ""
            for user_id in participants:
                value += f"<@{user_id}>\n"
            embed.add_field(
                name=f"Participants",
                value=value
            )
            author = await inter.bot.get_or_fetch_user(author_id)
            embed.set_author(name=author, icon_url=author.display_avatar.url)
            
            if len(participants) > 1:
                comps = [
                    disnake.ui.Button(label="Join", style=disnake.ButtonStyle.blurple, custom_id=f"{game_id}~roulettejoin~{author_id}~{bet}"),
                    disnake.ui.Button(label="Start", style=disnake.ButtonStyle.green, custom_id=f"{game_id}~roulettestart~{author_id}~{bet}"),
                    disnake.ui.Button(label="Rules", style=disnake.ButtonStyle.gray, custom_id=f"{author_id}~rouletterules"),
                    disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{author_id}~roulettequit"),
                ]
                await inter.response.edit_message(embed=embed, components=comps)
            else:
                await inter.response.edit_message(embed=embed)
        if button_id == "roulettestart": #Does not require game id
            author_id = int(id_parts[2])
            if inter.author.id == author_id: #Verify author
                print("ROULETTE START")
                game_id = id_parts[0]
                author_id = id_parts[2]
                bet = id_parts[3]
                participants = get_roulette_participants(game_id)
                original_participants = participants[:]
                temp_participants = participants[:]
                author = await inter.bot.get_or_fetch_user(author_id)
                ingame_comps = [
                    disnake.ui.Button(label="Join", style=disnake.ButtonStyle.blurple, disabled=True, custom_id=f"{game_id}~roulettejoin~{inter.author.id}~{bet}"),
                    disnake.ui.Button(label="Start", style=disnake.ButtonStyle.green, disabled=True, custom_id=f"{game_id}~roulettestart~{inter.author.id}~{bet}"),
                    disnake.ui.Button(label="Rules", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~rouletterules"),
                    disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, disabled=True, custom_id=f"{inter.author.id}~roulettequit"),
                ]
                await inter.response.edit_message()
                random.shuffle(temp_participants)
                while len(participants) > 1:
                    if(len(temp_participants) == 0):
                        temp_participants = participants[:]
                        random.shuffle(temp_participants)
                    target_user_id = int(temp_participants.pop(0))
                    embed = disnake.Embed(title=f"Russian Roulette!",description=f"A russian roulette game is in progress!\nBuy-in price: <:HonkaiCoin:997742624477818921> ~~**{bet}**~~\n\n<@{target_user_id}> has been chosen! :stopwatch:")
                    value = ""
                    for user_id in participants:
                        value += f"<@{user_id}>\n"
                    embed.add_field(
                        name=f"Participants Remaining",
                        value=value
                    )
                    embed.set_author(name=author, icon_url=author.display_avatar.url)
                    await inter.edit_original_message(embed=embed,components=ingame_comps)
                    
                    await asyncio.sleep(2)
                    
                    roll = random.randint(1,3) #NOTE: NOT 1 IN 6
                    if roll == 1: #dead
                        embed = disnake.Embed(title=f"Russian Roulette!",description=f"A russian roulette game is in progress!\nBuy-in price: <:HonkaiCoin:997742624477818921> ~~**{bet}**~~\n\n<@{target_user_id}> has **died!** :headstone:")
                        participants.remove(target_user_id)
                        update_balance(target_user_id, int(bet)*-1)
                    else:
                        embed = disnake.Embed(title=f"Russian Roulette!",description=f"A russian roulette game is in progress!\nBuy-in price: <:HonkaiCoin:997742624477818921> ~~**{bet}**~~\n\n<@{target_user_id}> has **survived!** :thumbsup:")
                        
                    value = ""
                    for user_id in participants:
                        value += f"<@{user_id}>\n"
                    embed.add_field(
                        name=f"Participants Remaining",
                        value=value
                    )
                    embed.set_author(name=author, icon_url=author.display_avatar.url)
                    await inter.edit_original_message(embed=embed,components=ingame_comps)
                    print(participants)
                    await asyncio.sleep(4)
                payout = int(bet)*(len(original_participants)-1)
                update_balance(participants[0], payout)
                embed = disnake.Embed(title=f"Russian Roulette!",description=f"A russian roulette game has concluded!\nBuy-in price: <:HonkaiCoin:997742624477818921> ~~**{bet}**~~\n\n<@{participants[0]}> has won the game!\n\nPrize: <:HonkaiCoin:997742624477818921> **{payout}**")
                value = ""
                for user_id in original_participants:
                    value += f"<@{user_id}>\n"
                embed.add_field(
                    name=f"Participants",
                    value=value
                )
                finished_comps = [
                    disnake.ui.Button(label="Join", style=disnake.ButtonStyle.blurple, disabled=True, custom_id=f"{game_id}~roulettejoin~{inter.author.id}~{bet}"),
                    disnake.ui.Button(label="Start", style=disnake.ButtonStyle.green, disabled=True, custom_id=f"{game_id}~roulettestart~{inter.author.id}~{bet}"),
                    disnake.ui.Button(label="Rules", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~rouletterules"),
                    disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~roulettequit"),
                ]
                embed.set_author(name=author, icon_url=author.display_avatar.url)
                await inter.edit_original_message(embed=embed,components=finished_comps)
        if button_id == "roulettequit": #Does not require game id
            author_id = int(id_parts[0])
            if inter.author.id == author_id: #Verify author
                await inter.response.defer()
                await inter.delete_original_message()
        if button_id == "rouletterules": #Does not require game id
            embed = disnake.Embed(
                title=f"Russian Roulette Rules",
                description=f"Pay the buy-in amount to enter a game.\n\nEach user takes a turn passing around a (fictional) revolver, pressing the trigger to their heads each turn.\n\nWhoever is the last one standing wins and takes the pot."
            )
            embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
            await inter.send(embed=embed, ephemeral=True)
                    
def setup(bot: commands.Bot):
    bot.add_cog(RouletteCommand(bot))