import disnake
from disnake.ext import commands
import random
import collections
import sqlite3
import os
from dotenv import load_dotenv
from data.economy_util import update_balance, get_balance
DB_PATH = os.getenv('DB_PATH')

deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

def finish(game_id: int):
    '''
    Updates the game state in the database.
    '''
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''UPDATE blackjack SET GAME_STATE = 0 WHERE GAME_ID={game_id};''')
    con.commit()
    con.close()

def convert_string(hand):
    '''
    Converts a hand to a string to be entered into the database.
    '''
    return ','.join([str(elem) for elem in hand])

def update_hands(game_id: int, player_hand, dealer_hand):
    '''
    Updates the hands in the database.
    '''
    player_hand_string = convert_string(player_hand)
    dealer_hand_string = convert_string(dealer_hand)
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    cur.execute(f'''UPDATE blackjack SET PLAYER_CARDS=?, DEALER_CARDS=? WHERE GAME_ID={game_id};''',(f"{player_hand_string}",f"{dealer_hand_string}"))
    con.commit()
    con.close()

def get_hands(game_id: int):
    '''
    Retrieves the hands from the database, and converts to a list format.
    '''
    con = sqlite3.connect(f"{DB_PATH}")
    cur = con.cursor()
    player_cards_string = cur.execute(f'''SELECT PLAYER_CARDS FROM blackjack WHERE GAME_ID={game_id};''')
    player_cards = player_cards_string.fetchone()[0].split(",")
    
    dealer_cards_string = cur.execute(f'''SELECT DEALER_CARDS FROM blackjack WHERE GAME_ID={game_id};''')
    dealer_cards = dealer_cards_string.fetchone()[0].split(",")
    con.commit()
    con.close()
    return player_cards, dealer_cards

def deal():
    '''
    Returns two random cards in a list. Used to initialize the game.
    '''
    global deck
    hand = []
    for i in range(2):
        random.shuffle(deck)
        card = deck[0]
        if card == 11:
            card = "J"
        if card == 12:
            card = "Q"
        if card == 13:
            card = "K"
        if card == 14:
            card = "A"
        hand.append(card)
    return hand

def total(hand):
    '''
    Sums the list of cards in a hand.
    '''
    total = 0
    for card in hand:
        if card == "J" or card == "Q" or card == "K":
            total += 10
        elif card == "A":
            if total >= 11:
                total+= 1
            else:
                total+= 11
        else:
            card = int(card)
            total += card
    return total

def hit(hand):
    '''
    Appends one random card to the hand.
    '''
    random.shuffle(deck)
    card = deck[0]
    if card == 11:
        card = "J"
    if card == 12:
        card = "Q"
    if card == 13:
        card = "K"
    if card == 14:
        card = "A"
    hand.append(card)
    return hand

def score(player_hand, dealer_hand):
    '''
    Calculates final results of the two hands.
    '''
    if total(dealer_hand) > 21: #dealer bust
        return "Player"
    elif total(player_hand) < total(dealer_hand): #dealer normal win
        return "Dealer"
    elif total(player_hand) > total(dealer_hand): #player normal win
        return "Player"
    else:
        return "Push"

def blackjack(player_hand, dealer_hand):
    '''
    Used only at the initial dealing of hands to check for immediate blackjack.
    '''
    if total(player_hand) == 21:
        return "Player"
    elif total(dealer_hand) == 21:
        return "Dealer"
    else:
        return "Neither"

def get_final_embed(inter, player_hand, dealer_hand, bet: int):
    embed = disnake.Embed(title=f"Bet: {bet}")
    embed.add_field(
        name=f"Player",
        value=f"{player_hand}\n**Total:** {total(player_hand)}"
    )
    embed.add_field(
        name=f"Dealer",
        value=f"{dealer_hand}\n**Total:** {total(dealer_hand)}"
    )
    embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
    return embed

def get_grayed_comps(inter):
    grayed_comps = [
        disnake.ui.Button(label="Hit", style=disnake.ButtonStyle.blurple, disabled=True), 
        disnake.ui.Button(label="Stand", style=disnake.ButtonStyle.green, disabled=True),
        disnake.ui.Button(label="Rules", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~blackjackrules"),
        disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~blackjackquit"),
    ]
    return grayed_comps

class BlackjackCommand(commands.Cog):
    # Note that we're using self as the first argument, since the command function is inside a class.
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.slash_command(
        name="blackjack",
        description="Plays blackjack.",
        # guild_ids=[1234, 5678]
    )
    async def blackjack(self, inter: disnake.ApplicationCommandInteraction, bet: int = 0):
        player_balance = get_balance(inter.author.id)
        if(bet > player_balance):
            await inter.response.send_message(f"Insufficient balance!", ephemeral=True)
            return
        player_hand = deal()
        dealer_hand = deal()
        player_hand_string = convert_string(player_hand)
        dealer_hand_string = convert_string(dealer_hand)

        #Check for instant win/loss
        winner = blackjack(player_hand,dealer_hand)
        if not winner == "Neither":
            if winner == "Player":
                description = "Player wins!"
                update_balance(inter.author.id, bet)
            else:
                description = "Player loses..."
                update_balance(inter.author.id, bet*-1)
            embed = disnake.Embed(
                title=f"Bet: {bet}",
                description=description
            )
            embed.add_field(
                name=f"Player",
                value=f"{player_hand}\n**Total:** {total(player_hand)}"
            )
            embed.add_field(
                name=f"Dealer",
                value=f"{dealer_hand}\n**Total:** {total(dealer_hand)}"
            )
            grayed_comps = [
                disnake.ui.Button(label="Hit", style=disnake.ButtonStyle.blurple, disabled=True), 
                disnake.ui.Button(label="Stand", style=disnake.ButtonStyle.green, disabled=True),
                disnake.ui.Button(label="Rules", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~blackjackrules"),
                disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~blackjackquit"),
            ]
            embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
            
            await inter.response.send_message(embed=embed, components=grayed_comps)
            return
        embed = disnake.Embed(title=f"Bet: {bet}")
        embed.add_field(
            name=f"Player",
            value=f"{player_hand}\n**Total:** {total(player_hand)}"
        )
        embed.add_field(
            name=f"Dealer",
            value=f"{dealer_hand[0]}"
        )
        embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
        
        con = sqlite3.connect(f"{DB_PATH}")
        print("---------------CONNECTED---------------")
        cur = con.cursor()
        cur.execute(f'''INSERT INTO blackjack (PLAYER_ID,PLAYER_CARDS,DEALER_CARDS) 
                    values ({inter.author.id},"{player_hand_string}","{dealer_hand_string}");''')
        cur.execute(f'''SELECT last_insert_rowid() FROM blackjack;''')
        game_id = cur.fetchone()[0]
        con.commit()
        con.close()
        
        comps = [
            disnake.ui.Button(label="Hit", style=disnake.ButtonStyle.blurple, custom_id=f"{game_id}~blackjackhit~{inter.author.id}~{bet}"),
            disnake.ui.Button(label="Stand", style=disnake.ButtonStyle.green, custom_id=f"{game_id}~blackjackstand~{inter.author.id}~{bet}"),
            disnake.ui.Button(label="Rules", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~blackjackrules"),
            disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~blackjackquit"),
        ]
        await inter.response.send_message(embed=embed, components=comps)
        #Game is now in default play state
    
    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        id_parts = inter.component.custom_id.split('~')
        button_id = id_parts[1]
        global deck
        if button_id == "blackjackhit": #Requires game id
            author_id = int(id_parts[2])
            if inter.author.id == author_id: #Verify author
                game_id = id_parts[0]
                bet = int(id_parts[3])
                
                hands = get_hands(game_id)
                player_hand = hands[0]
                dealer_hand = hands[1]
                
                hit(player_hand)
                
                update_hands(game_id, player_hand, dealer_hand)
                
                embed = disnake.Embed(title=f"Bet: {bet}")
                embed.add_field(
                    name=f"Player",
                    value=f"{player_hand}\n**Total:** {total(player_hand)}"
                )
                embed.add_field(
                    name=f"Dealer",
                    value=f"{dealer_hand[0]}"
                )
                if total(player_hand) > 21:
                    embed = get_final_embed(inter, player_hand, dealer_hand, bet)
                    grayed_comps = get_grayed_comps(inter)
                    await inter.response.edit_message(embed=embed, components=grayed_comps)
                    update_balance(inter.author.id, bet*-1)
                    finish(game_id)
                    return
                embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
                await inter.response.edit_message(embed=embed)
        if button_id == "blackjackstand": #Requires game id
            author_id = int(id_parts[2])
            if inter.author.id == author_id: #Verify author
                game_id = id_parts[0]
                bet = int(id_parts[3])
                
                hands = get_hands(game_id)
                player_hand = hands[0]
                dealer_hand = hands[1]
                
                while total(dealer_hand) < 17:
                    hit(dealer_hand)
                
                update_hands(game_id, player_hand, dealer_hand)
                
                embed = get_final_embed(inter, player_hand, dealer_hand, bet)
                grayed_comps = get_grayed_comps(inter)
                
                result = score(player_hand, dealer_hand)
                if result == "Player":
                    embed.description = f"Player wins!"
                    update_balance(inter.author.id, bet)
                elif result == "Dealer":
                    embed.description = f"Player loses..."
                    update_balance(inter.author.id, bet*-1)
                else:
                    embed.description = f"Push!"
                await inter.response.edit_message(embed=embed, components=grayed_comps)
                finish(game_id)
                return
        if button_id == "blackjackquit": #Does not require game id
            author_id = int(id_parts[0])
            if inter.author.id == author_id: #Verify author
                game_id = id_parts[0]
                await inter.response.defer()
                await inter.delete_original_message()
                finish(game_id)
                return
        if button_id == "blackjackrules": #Does not require game id
            author_id = int(id_parts[0])
            if inter.author.id == author_id: #Verify author
                embed = disnake.Embed(
                    title=f"Blackjack Rules",
                    description=f"Get as close to 21 as possible without going over!\nAces are worth 1 or 11, and face cards are worth 10!"
                )
                embed.add_field(
                    name=f"Hit",
                    value=f"Draw one card."
                )
                embed.add_field(
                    name=f"Stand",
                    value=f"Finalize your cards."
                )
                embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
                await inter.send(embed=embed, ephemeral=True)
                return
def setup(bot: commands.Bot):
    bot.add_cog(BlackjackCommand(bot))