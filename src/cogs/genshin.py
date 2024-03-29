import disnake
from disnake.ext import commands
import random
import collections
import sqlite3
import os
from dotenv import load_dotenv
from data.genshin_util import insert_pull, get_pulls, reset_pulls, get_pity, set_pity5, set_pity4

players = {}
instances = {} #user id and message id

_5Stars = {
    "Keqing": "<:Keqing:994625518475411507>",
    "Mona" : "<:Mona:994625514725720084>",
    "Qiqi" : "<:Qiqi:994625517695287316>",
    "Jean" : "<:Jean:994625516894175282>",
    "Diluc" : "<:Diluc:994625515459719180>",
    
    "Amos Bow": "<:Amos_Bow:994623953505091604>",
    "Skyward Harp" : "<:Skyward_Harp:994623952552988742>",
    "Lost Prayer To The Sacred Winds" : "<:Lost_Prayer_To_The_Sacred_Winds:994623946777432074>",
    "Skyward Atlas" : "<:Skyward_Atlas:994623951105962096>",
    "Primordial Jade Winged-Spear" : "<:Primordial_Jade_WingedSpear:994623945405890580>",
    "Skyward Spine" : "<:Skyward_Spine:994623950220967956>",
    "Wolf's Gravestone" : "<:Wolfs_Gravestone:994623944298610828>",
    "Skyward Pride" : "<:Skyward_Pride:994623949168201800> ",
    "Skyward Blade" : "<:Skyward_Blade:994623947981213746>",
    "Aquila Favonia" : "<:Aquila_Favonia:994623943036129312>",
}
_4Stars = {
    "Sucrose" : "<:Sucrose:994629336399360150>",
    "Chongyun" : "<:Chongyun:994629334088286259>",
    "Noelle" : "<:Noelle:994629335258501190>",
    "Bennett" : "<:Bennett:994629328254025769>",
    "Fischl" : "<:Fischl:994629329206128640>",
    "Ningguang" : "<:Ningguang:994629332070826004>",
    "Xingqiu" : "<:Xingqiu:994629330175008829>",
    "Beidou" : "<:Beidou:994629333098446858>",
    "Xiangling" : "<:Xiangling:994629331034841168>",
    "Amber" : "<:Amber:994629342997008474>",
    "Razor" : "<:Razor:994629327448711308> ",
    "Kaeya" : "<:Kaeya:994629325091512350>",
    "Barbara" : "<:Barbara:994629326467248158>",
    "Lisa" : "<:Lisa:994629344259493909>",
    "Sayu" : "<:Sayu:994629338395852872>",
    "Diona" : "<:Diona:994629342011346948>",
    "Rosaria" : "<:Rosaria:994629345601671238> ",
    "Kujou Sara" : "<:Sara:994629337041084489>",
    "Gorou" : "<:Gorou:994631989418283158>",
    "Yun Jin" : "<:YunJin:994631990814973992> ",
    "Thoma" : "<:Thoma:994629339205341284>",
    "Xinyan" : "<:Xinyan:994629341084405800>",
    "Yanfei" : "<:Yanfei:994629340199399434>",
    
    "Rust" : "<:Rust:994632935913291906>",
    "Sacrificial Bow" : "<:Sacrificial_Bow:994632934667595857> ",
    "The Stringless" : "<:The_Stringless:994632930401992734>",
    "Favonius Warbow" : "<:Favonius_Warbow:994632926903943188>",
    "Eye Of Perception" : "<:Eye_Of_Perception:994632919031226469>",
    "Sacrificial Fragments" : "<:Sacrificial_Fragments:994632933468024832> ",
    "The Widsith" : "<:The_Widsith:994632929630236834> ",
    "Favonius Codex" : "<:Favonius_Codex:994632924873896028>",
    "Favonius Lance" : "<:Favonius_Lance:994632925951836290>",
    "Dragon's Bane" : "<:Dragons_Bane:994632922038554775>",
    "Rainslasher" : "<:Rainslasher:994632921182896218>",
    "Sacrificial Greatsword" : "<:Sacrificial_Greatsword:994632932318793778>",
    "The Bell" : "<:The_Bell:994632928405495899>",
    "Favonius Greatsword" : "<:Favonius_Greatsword:994632923967914095>",
    "Lions Roar" : "<:Lions_Roar:994632920134324255>",
    "Sacrificial Sword" : "<:Sacrificial_Sword:994632931341512774>",
    "The Flute" : "<:The_Flute:994632927549870201>",
    "Favonius Sword" : "<:Favonius_Sword:994632922927726602> ",
}
# Not giving 3 stars images
_3Stars = [
    "Slingshot",
    "Sharpshooter's Oath",
    "Raven Bow",
    "Emerald Orb",
    "Thrilling Tales Of Dragon Slayers",
    "Magic Guide",
    "Black Tassel",
    "Debate Club",
    "Bloodtainted Greatsword",
    "Ferrous Shadow",
    "Skyrider Sword",
    "Harbinger Of Dawn",
    "Cool Steel",
]

pity4 = 0
    
def getPull(rarity):
    if rarity == 5:
        return random.choice(list(_5Stars.keys()))
    elif rarity == 4:
        return random.choice(list(_4Stars.keys()))
    else:
        l = len(_3Stars) -1 
        num = random.randint(0,l)
        pull = _3Stars[num]
        return pull

def wish(amount, pity5, pity4):
    stuffGot = [];
    for val in range(0,amount):
        if pity5 >= 89:
            pull = getPull(5)
            stuffGot.append(pull)
            pity5  = 0
            pity4 += 1
        elif pity4 >= 9:
            pull = getPull(4)
            stuffGot.append(pull)
            pity5 += 1
            pity4  = 0
        else:
            num = random.randint(0,1000)
            if pity5 >= 85:
                if num >= 994:
                    pull = getPull(5)
                    stuffGot.append(pull)
                    pity5 = 0
                    continue
            elif pity5 >= 80:
                if num >= 984:
                    pull = getPull(5)
                    stuffGot.append(pull)
                    pity5 = 0
                    continue
            elif pity5 >= 75:
                if num >= 920:
                    pull = getPull(5)
                    stuffGot.append(pull)
                    pity5 = 0
                    continue
            else:
                if num >= 994:
                    pull = getPull(5)
                    stuffGot.append(pull)
                    pity5 = 0
                    continue
            if num >= 943:
                pull = getPull(4)
                stuffGot.append(pull)
                pity5 += 1
                pity4  = 0
            else :
                pull = getPull(3)
                stuffGot.append(pull)
                pity5 += 1
                pity4 += 1
    return stuffGot, pity5, pity4

class GenshinCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.slash_command()
    async def genshin(self, inter: disnake.ApplicationCommandInteraction):
        """
        Genshin Impact Panel
        """
        comps = [
            disnake.ui.Button(label="Wish", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~wish"),
            disnake.ui.Button(label="Wish x10", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~wish10"),
            disnake.ui.Button(label="Reset Embed", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~resetwish"),
            disnake.ui.Button(label="Inventory", style=disnake.ButtonStyle.green, custom_id=f"{inter.author.id}~inventorywish"),
            disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~quitwish")
        ]
        embed = disnake.Embed(
            title="Genshin Wishing Simulator",
            description="Press any button to begin!"
        )
        embed.set_thumbnail(f"{inter.author.avatar}")
        embed.set_author(name=f"{inter.author}", icon_url=f"{inter.author.display_avatar.url}")
        await inter.response.send_message(components=comps, embed=embed)
    
    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        global _5Stars
        global _4Stars
        global _3Stars
        id_parts = inter.component.custom_id.split('~')
        
        button_id = id_parts[1]
        
        if button_id == "wish":
            author_id = int(id_parts[0])
            if author_id == inter.author.id:
                await inter.response.defer()
                pity = get_pity(inter.author.id)
                pity5 = pity[0]
                pity4 = pity[1]
                
                wish_results = wish(1, pity5, pity4)
                items = wish_results[0]
                new_pity5 = wish_results[1]
                new_pity4 = wish_results[2]
                set_pity5(inter.author.id, new_pity5)
                set_pity4(inter.author.id, new_pity4)
                
                description = ""
                for item in items:
                    insert_pull(inter.author.id, item)
                    
                    emoji_id = ""
                    if item in _5Stars.keys():
                        emoji_id = _5Stars[item]
                        item = f">>>__**{item}**__<<<"
                    elif item in _4Stars.keys():
                        emoji_id = _4Stars[item]
                        item = f"**{item}**"
                    else:
                        emoji_id = ""
                    description += f"{item} {emoji_id}\n"
                description += f"\n**Pity: {new_pity5}**"
                
                comps = [
                    disnake.ui.Button(label="Wish", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~wish"),
                    disnake.ui.Button(label="Wish x10", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~wish10"),
                    disnake.ui.Button(label="Reset Embed", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~resetwish"),
                    disnake.ui.Button(label="Inventory", style=disnake.ButtonStyle.green, custom_id=f"{inter.author.id}~inventorywish"),
                    disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~quitwish")
                ]
                embed = disnake.Embed(
                    title="Genshin Wishing Simulator",
                    description=description
                )
                embed.set_thumbnail(f"{inter.author.avatar}")
                embed.set_author(name=f"{inter.author}", icon_url=f"{inter.author.display_avatar.url}")
                await inter.edit_original_message(embed=embed, components=comps)
        if button_id == "wish10":
            author_id = int(id_parts[0])
            if author_id == inter.author.id:
                await inter.response.defer()
                pity = get_pity(inter.author.id)
                pity5 = pity[0]
                pity4 = pity[1]
                
                wish_results = wish(10, pity5, pity4)
                items = wish_results[0]
                new_pity5 = wish_results[1]
                new_pity4 = wish_results[2]
                set_pity5(inter.author.id, new_pity5)
                set_pity4(inter.author.id, new_pity4)

                description = ""
                for item in items:
                    insert_pull(inter.author.id, item)
                    
                    emoji_id = ""
                    if item in _5Stars.keys():
                        emoji_id = _5Stars[item]
                        item = f">>>**{item}**<<<"
                    elif item in _4Stars.keys():
                        emoji_id = _4Stars[item]
                        item = f"**{item}**"
                    else:
                        emoji_id = ""
                    description += f"{item} {emoji_id}\n"
                description += f"\n**Pity: {new_pity5}**"
                
                comps = [
                    disnake.ui.Button(label="Wish", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~wish"),
                    disnake.ui.Button(label="Wish x10", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~wish10"),
                    disnake.ui.Button(label="Reset Embed", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~resetwish"),
                    disnake.ui.Button(label="Inventory", style=disnake.ButtonStyle.green, custom_id=f"{inter.author.id}~inventorywish"),
                    disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~quitwish")
                ]
                embed = disnake.Embed(
                    title="Genshin Wishing Simulator",
                    description=description
                )
                embed.set_thumbnail(f"{inter.author.avatar}")
                embed.set_author(name=f"{inter.author}", icon_url=f"{inter.author.display_avatar.url}")
                await inter.edit_original_message(embed=embed, components=comps)
        if button_id == "resetwish":
            author_id = int(id_parts[0])
            if author_id == inter.author.id:
                await inter.response.defer()
                comps = [
                    disnake.ui.Button(label="Wish", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~wish"),
                    disnake.ui.Button(label="Wish x10", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~wish10"),
                    disnake.ui.Button(label="Reset Embed", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~resetwish"),
                    disnake.ui.Button(label="Inventory", style=disnake.ButtonStyle.green, custom_id=f"{inter.author.id}~inventorywish"),
                    disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~quitwish")
                ]
                embed = disnake.Embed(
                    title="Genshin Wishing Simulator",
                    description="Press any button to begin!"
                )
                embed.set_thumbnail(f"{inter.author.avatar}")
                embed.set_author(name=f"{inter.author}", icon_url=f"{inter.author.display_avatar.url}")
                await inter.edit_original_message(embed=embed,components=comps)
        if button_id == "quitwish":
            author_id = int(id_parts[0])
            if author_id == inter.author.id:
                await inter.response.defer()
                await inter.delete_original_message()
        if button_id == "inventorywish":
            author_id = int(id_parts[0])
            if author_id == inter.author.id:
                await inter.response.defer()
                dict5 = {}
                dict4 = {}
                dict3 = {}
                pulls = get_pulls(inter.author.id)
                for item in pulls:
                    if item in _5Stars.keys():
                        if item in dict5.keys():
                            dict5[item] += 1
                        else:
                            dict5[item] = 1
                    elif item in _4Stars.keys():
                        if item in dict4.keys():
                            dict4[item] += 1
                        else:
                            dict4[item] = 1
                    else:
                        if item in dict3.keys():
                            dict3[item] += 1
                        else:
                            dict3[item] = 1
                embed = disnake.Embed(
                    title=f"{inter.author.name}'s Inventory"
                )
                value = ""
                for item in dict5:
                    value += f"(**{dict5[item]}**) {_5Stars[item]}{item} \n"
                value += "\n"
                for item in dict4:
                    value += f"(**{dict4[item]}**) {_4Stars[item]}{item} \n"
                value += "\n"
                for item in dict3:
                    value += f"(**{dict3[item]}**) {item} \n"
                embed.description = value
                comps = [
                    disnake.ui.Button(label="Wish", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~wish"),
                    disnake.ui.Button(label="Wish x10", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~wish10"),
                    disnake.ui.Button(label="Reset Embed", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~resetwish"),
                    disnake.ui.Button(label="Inventory", style=disnake.ButtonStyle.green, custom_id=f"{inter.author.id}~inventorywish"),
                    disnake.ui.Button(label="Quit", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~quitwish")
                ]
                await inter.edit_original_message(embed=embed,components=comps)

def setup(bot: commands.Bot):
    bot.add_cog(GenshinCommand(bot))