import disnake
from disnake.ext import commands
import random
import collections
import sqlite3

con = sqlite3.connect('../db/database.db')

deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]*4
players = {} # player id : player & dealer deck

def deal(deck):
    '''
    Deals two cards. Used to initialize the game.
    '''
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
    Sums the cards in a hand.
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
            total += card
    return total

def hit(hand):
    card = deck.pop()
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

def blackjack(dealer_hand, player_hand):
    '''
    Used only at the initial dealing of hands to check for immediate blackjack.
    '''
    if total(player_hand) == 21:
        return "Player"
    
    elif total(dealer_hand) == 21:
        return "Dealer"
    else:
        return "Neither"


def custom_cooldown(message):
    return commands.Cooldown(1, 10)  # 1 per 10 secs


class BlackjackCommand(commands.Cog):
    # Note that we're using self as the first argument, since the command function is inside a class.
    def __init__(self, bot: commands.Bot):
        self.bot = bot
    
    @commands.slash_command(
        name="blackjack",
        description="Plays blackjack.",
        # guild_ids=[1234, 5678]
    )
    async def blackjack(self, inter: disnake.ApplicationCommandInteraction):#, bet: int):
        global deck
        global players
        # if inter.author.id not in balances.keys():
        #     balances[inter.author.id] = 100
        # if balances[inter.author.id] < bet:
        #     inter.response.send_message(content=f"You do not have enough money to bet {bet}!")
        #     return
        players[inter.author.id] = {}
        players[inter.author.id][0] = deal(deck=deck)
        players[inter.author.id][1] = deal(deck=deck)
        # NOTE: player_hand is players[inter.author.id][0], and dealer_hand is players[inter.author.id][1]
        comps = [
            disnake.ui.Button(label="Hit", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~blackjackhit"),#~{bet}"),
            disnake.ui.Button(label="Stand", style=disnake.ButtonStyle.green, custom_id=f"{inter.author.id}~blackjackstand"),#~{bet}"),
            disnake.ui.Button(label="Rules", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~blackjackrules"),
            disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~blackjackquit"),
        ]
        #If instant blackjack
        if not blackjack(players[inter.author.id][1],players[inter.author.id][0]) == "Neither":
                winner = blackjack(players[inter.author.id][1],players[inter.author.id][0])
                description = ""
                if winner == "Player":
                    description = "Player wins!"# (+{bet})"
                    # balances[inter.author.id] += bet
                else:
                    description = "Player loses..."# (-{bet})"
                    # balances[inter.author.id] -= bet
                embed = disnake.Embed(
                    title=f"",
                    description=description
                )
                embed.add_field(
                    name=f"Player",
                    value=f"{players[inter.author.id][0]}\n**Total:** {total(players[inter.author.id][0])}"
                )
                embed.add_field(
                    name=f"Dealer",
                    value=f"{players[inter.author.id][1]}\n**Total:** {total(players[inter.author.id][1])}"
                )
                grayed_comps = [
                    disnake.ui.Button(label="Hit", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~blackjackhit", disabled=True), 
                    disnake.ui.Button(label="Stand", style=disnake.ButtonStyle.green, custom_id=f"{inter.author.id}~blackjackstand", disabled=True),
                    disnake.ui.Button(label="Rules", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~blackjackrules"),
                    disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~blackjackquit"),
                ]
                embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
                
                await inter.response.send_message(embed=embed, components=grayed_comps)
                return
        embed = disnake.Embed(
            title=f"",
            description=f"" #f"Bet: {bet}"
        )
        embed.add_field(
            name=f"Player",
            value=f"{players[inter.author.id][0]}\n**Total:** {total(players[inter.author.id][0])}"
        )
        embed.add_field(
            name=f"Dealer",
            value=f"{players[inter.author.id][1][0]}"
        )
        embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
        await inter.response.send_message(embed=embed, components=comps)
        #Game is now in default play state
    
    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        id_parts = inter.component.custom_id.split('~')
        author_id = int(id_parts[0])
        button_id = id_parts[1]
        global deck
        global players
        if button_id == "blackjackhit":
            if inter.author.id == author_id: #Verify author
                hit(players[inter.author.id][0])
                # bet = int(id_parts[2])
                embed = disnake.Embed(
                    title=f"",
                    description=f"" #f"Bet: {bet}"
                )
                embed.add_field(
                    name=f"Player",
                    value=f"{players[inter.author.id][0]}\n**Total:** {total(players[inter.author.id][0])}"
                )
                embed.add_field(
                    name=f"Dealer",
                    value=f"{players[inter.author.id][1][0]}"
                )
                
                if total(players[inter.author.id][0]) > 21:
                        embed.description = f"Player loses..."# (-{bet})"
                        grayed_comps = [
                            disnake.ui.Button(label="Hit", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~blackjackhit", disabled=True), 
                            disnake.ui.Button(label="Stand", style=disnake.ButtonStyle.green, custom_id=f"{inter.author.id}~blackjackstand", disabled=True),
                            disnake.ui.Button(label="Rules", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~blackjackrules"),
                            disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~blackjackquit"),
                        ]
                        embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
                        # balances[inter.author.id] -= bet
                        await inter.response.edit_message(embed=embed, components=grayed_comps)
                        return
                embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
                await inter.response.edit_message(embed=embed)
        if button_id == "blackjackstand":
            if inter.author.id == author_id: #Verify author
                # bet = int(id_parts[2])
                while total(players[inter.author.id][1]) < 17:
                    hit(players[inter.author.id][1])
                    
                embed = disnake.Embed(
                    title=f"",
                    description=f"" #f"Bet: {bet}"
                )
                embed.add_field(
                    name=f"Player",
                    value=f"{players[inter.author.id][0]}\n**Total:** {total(players[inter.author.id][0])}"
                )
                embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
                embed.add_field(
                    name=f"Dealer",
                    value=f"{players[inter.author.id][1]}\n**Total:** {total(players[inter.author.id][1])}"
                )
                grayed_comps = [
                    disnake.ui.Button(label="Hit", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~blackjackhit", disabled=True), 
                    disnake.ui.Button(label="Stand", style=disnake.ButtonStyle.green, custom_id=f"{inter.author.id}~blackjackstand", disabled=True),
                    disnake.ui.Button(label="Rules", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~blackjackrules"),
                    disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~blackjackquit"),
                ]
                
                result = score(players[inter.author.id][0], players[inter.author.id][1])
                if result == "Player":
                    embed.description = f"Player wins!"# (+{bet})"
                    # balances[inter.author.id] += bet
                elif result == "Dealer":
                    embed.description = f"Player loses..."# (-{bet})"
                    # balances[inter.author.id] -= bet
                else:
                    embed.description = f"Push!"
                await inter.response.edit_message(embed=embed, components=grayed_comps)
                return
        if button_id == "blackjackquit":
            if inter.author.id == author_id: #Verify author
                await inter.response.defer()
                await inter.delete_original_message()
                return
        if button_id == "blackjackrules":
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