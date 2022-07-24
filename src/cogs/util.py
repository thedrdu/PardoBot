from distutils.command.config import config
from typing import Counter
import disnake
import google_images_search
from google_images_search import GoogleImagesSearch
import fandom
import tweepy
import json
import requests
from tqdm import tqdm
import os
import io
import aiohttp
import asyncio
import collections
import itertools
import genshin
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from disnake.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta
from data.general_util import set_reminder, get_reminder, create_poll, insert_option, remove_vote, add_vote, get_options, get_votes, get_user_description, set_user_description, set_honkai_user_info, get_honkai_user_info
GCS_DEVELOPER_KEY = os.getenv('GCS_DEVELOPER_KEY')
GCS_CX = os.getenv('GCS_CX')
TWT_API_KEY = os.getenv('TWT_API_KEY')
TWT_API_KEY_SECRET = os.getenv('TWT_API_KEY_SECRET')
TWT_BEARER_TOKEN = os.getenv('TWT_BEARER_TOKEN')
TWT_ACCESS_TOKEN = os.getenv('TWT_ACCESS_TOKEN')
TWT_ACCESS_TOKEN_SECRET = os.getenv('TWT_ACCESS_TOKEN_SECRET')

# scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
# os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
# api_service_name = "youtube"
# api_version = "v3"
# client_secrets_file = "client_secret_666813241337-86h24s6mfge7u9f3862mi8bdna4su66r.apps.googleusercontent.com.json"
# flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
# credentials = flow.run_console()
# youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)

gis = GoogleImagesSearch(GCS_DEVELOPER_KEY, GCS_CX)
fandom.set_wiki("honkaiimpact3")

twt_auth = tweepy.OAuthHandler(TWT_API_KEY, TWT_API_KEY_SECRET)
twt_auth.set_access_token(TWT_ACCESS_TOKEN, TWT_ACCESS_TOKEN_SECRET)
api = tweepy.API(twt_auth)
twt_username='thedrdu'

def _get_single_video_data(self, video_id, part):
    #part can be 'snippet', 'statistics', 'contentDetails', 'topicDetails'
    url = f"https://www.googleapis.com/youtube/v3/videos?part={part}&id={video_id}&key=AIzaSyBnQDgW_vSiauko7UfVbZL7syKW1ghjBNY"
    json_url = requests.get(url)
    data = json.loads(json_url.text)
    data = data['items'][0][part]
    return data

class UtilCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check.start()
    
    @tasks.loop(seconds=60.0)
    async def check(self):
        # tweets_list= api.home_timeline()
        # tweet= tweets_list[0]
        # print(tweet.text)
        ''' Reminders '''
        data = get_reminder()
        reminders = data[0]
        creation_times = data[1]
        for user_id in reminders:
            user = await self.bot.get_or_fetch_user(user_id)
            embed = disnake.Embed(
                title=f"Reminder for {user.name}",
                description=f"{reminders[user_id]}",
                colour=0xFF0000
            )
            embed.set_author(name=user, icon_url=user.display_avatar.url)
            embed.set_thumbnail(user.avatar)
            embed.set_footer(text=f"Reminder created at {creation_times[user.id]}")
            await user.send(embed=embed)
    
    @commands.slash_command(
        name="latestvideo",
        description="Returns the latest video from the official HI3 YouTube channel."
    )
    async def latestvideo(self, inter: disnake.ApplicationCommandInteraction):
        url = f'https://www.googleapis.com/youtube/v3/channels?part=statistics&id=UCko6H6LokKM__B03i5_vBQQ&key={GCS_DEVELOPER_KEY}'
        json_url = requests.get(url)
        data = json.loads(json_url.text)['items'][0]['statistics']
        
        channel_videos = {}
        url = f"https://www.googleapis.com/youtube/v3/search?key={GCS_DEVELOPER_KEY}&channelId=UCko6H6LokKM__B03i5_vBQQ&part=snippet,id&order=date"
        json_url = requests.get(url)
        data = json.loads(json_url.text)
        item_data = data['items']
        for item in item_data:
            kind = item['id']['kind']
            if kind == 'youtube#video':
                published_at = item['snippet']['publishedAt']
                title = item['snippet']['title']
                video_id = item['id']['videoId']
                channel_videos[video_id] = {'publishedAt': published_at, 'title': title}
        await inter.response.send_message(content=f"Latest video from HI3 YouTube channel: https://www.youtube.com/watch?v={list(channel_videos)[0]}")
    
    
    @commands.slash_command(
        name="statsconfig",
        description="Configure user HoYoLAB profile on PardoBot.",
    )
    async def statsconfig(self, inter: disnake.ApplicationCommandInteraction, ltuid: int, ltoken: str, honkai_uid: int):
        set_honkai_user_info(inter.author.id,ltuid,ltoken,honkai_uid)
        await inter.response.send_message(content=f"Successfully set user info!",ephemeral=True)
    
    @commands.slash_command(
        name="stats",
        description="Retrieves user's HI3 stats.",
    )
    async def stats(self, inter: disnake.ApplicationCommandInteraction):
        user_data = get_honkai_user_info(inter.author.id)
        if user_data is None:
            await inter.response.send_message(content=f"User profile not yet configured! (Try `/statsconfig`)",ephemeral=True)
            return
        cookies = {"ltuid": user_data[0], "ltoken": user_data[1]}
        client = genshin.Client(cookies)
        user = await client.get_honkai_user(user_data[2])
        embed = disnake.Embed(
            title=f"{user.info.nickname}'s Profile",
            description=f"**Level**: {user.info.level}\n**Server**: {user.info.server}\n**Active Days**: {user.stats.active_days}",
            color=0x0000FF
        )
        embed.add_field(
            name=f"Battlesuits Owned",value=f"{user.stats.battlesuits} (<:Valkyrie_S3:1000596833527136276> {user.stats.battlesuits_SSS})"
        )
        embed.add_field(
            name=f"Outfits Owned",value=user.stats.outfits
        )
        embed.add_field(
            name=f"Elysian Realm",value=f"High Score: {user.stats.elysian_realm.highest_score}"
        )
        embed.add_field(
            name=f"Prev. Memorial Arena",value=f"Rank: {user.stats.memorial_arena.ranking}%\nScore: {user.stats.memorial_arena.score}"
        )
        embed.add_field(
            name=f"Prev. Infinity Abyss",value=f"Rank: {user.stats.abyss.raw_q_singularis_rank} ({user.stats.abyss.latest_type})\nScore: {user.stats.abyss.score}"
        )
        embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
        embed.set_thumbnail(url=inter.author.avatar.url)
        embed.set_footer(text=f"Data retrieved in {round(inter.bot.latency * 1000)}ms")
        await inter.response.send_message(embed=embed)
    
    @commands.slash_command(
        name="wikisearch",
        description="Searches the HI3 Wikia.",
    )
    async def wikisearch(self, inter: disnake.ApplicationCommandInteraction, query: str):
        await inter.response.defer()
        search_results = fandom.search(query, results=1)
        if len(search_results) == 0:
            embed = disnake.Embed(title=f"No Pages Found!",description=f"No pages were found for: **{query}**.")
            await inter.edit_original_message(embed=embed)
            return
        page_title = search_results[0][0]
        page = fandom.page(title= page_title)
        # print(page.html)
        summary = page.summary
        if len(summary) > 2000:
            summary = page.summary[0:1999]
        embed = disnake.Embed(
            title=page.title,
            description=f"**Summary:** {summary}",
            color=0x0000FF
        )
        page_button = disnake.ui.Button(label="Open Page", style=disnake.ButtonStyle.blurple,url=page.url)
        if len(page.sections) == 0:
            sections = f"**None**"
        else:
            sections = '\n'.join(page.sections)
        embed.add_field(name=f"Sections",value=f"{sections}")
        
        search_params = {
            'q': f"honkai impact 3rd {query}",
            'num': 1,
            # 'fileType': 'jpg|gif|png',
            # 'rights': 'cc_publicdomain|cc_attribute|cc_sharealike|cc_noncommercial|cc_nonderived',
        }
        gis.search(search_params=search_params)
        
        embed.set_thumbnail(url=gis.results()[0].url)
        embed.set_footer(text=f"Data obtained from Honkai Impact 3 Wikia and Google Images in {round(inter.bot.latency * 1000)}ms")
        await inter.edit_original_message(embed=embed,components=page_button)
    
    
    
    @commands.slash_command(
        name="remindme",
        description="Sets a reminder.",
    )
    async def remindme(self, inter: disnake.ApplicationCommandInteraction, reminder: str, days: int = 0, hours: int = 0, minutes: int = 0):
        reminder_time = datetime.now() + timedelta(days=days, hours=hours, minutes=minutes)
        set_reminder(inter.author.id, reminder, reminder_time.strftime("%Y:%m:%d:%H:%M"), datetime.now().strftime("%Y:%m:%d:%H:%M"))
        await inter.response.send_message(content=f"Reminder successfully set!", ephemeral=True)
        
    @commands.slash_command(
        name="pfp",
        description="Returns a target user's profile picture.",
    )
    async def pfp(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User):
        await inter.response.defer()
        async with aiohttp.ClientSession() as session:
            async with session.get(user.avatar.url) as resp:
                if resp.status != 200:
                    return await inter.send('Could not download file...')
                data = io.BytesIO(await resp.read())
        await inter.send(file=disnake.File(data, filename=f"{user.name}.png"))
    
    @commands.slash_command(
        name="poll",
        description="Sends a poll embed.",
        guild_only=True,
    )
    async def poll(self, inter: disnake.ApplicationCommandInteraction, title: str, option1: str, option2: str, option3: str = None, option4: str = None, option5: str = None):
        '''
        2 options are required. A poll can contain up to 5 options.
        '''
        option_names = ""
        comps = []
        
        poll_id = create_poll(title)
        option1_id = insert_option(poll_id, option1)
        option_names += f"{option1}: 0\n"
        option2_id = insert_option(poll_id, option2)
        option_names += f"{option2}: 0\n"
        comps.append(disnake.ui.Button(label=f"{option1}", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~pollvote~{poll_id}~{option1_id}"))
        comps.append(disnake.ui.Button(label=f"{option2}", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~pollvote~{poll_id}~{option2_id}"))
        
        if not option3 is None:
            option3_id = insert_option(poll_id, option3)
            option_names += f"{option3}: 0\n"
            comps.append(disnake.ui.Button(label=f"{option3}", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~pollvote~{poll_id}~{option3_id}"))
        if not option4 is None:
            option4_id = insert_option(poll_id, option4)
            option_names += f"{option4}: 0\n"
            comps.append(disnake.ui.Button(label=f"{option4}", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~pollvote~{poll_id}~{option4_id}"))
        if not option5 is None:
            option5_id = insert_option(poll_id, option5)
            option_names += f"{option5}: 0\n"
            comps.append(disnake.ui.Button(label=f"{option5}", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~pollvote~{poll_id}~{option5_id}"))

        embed = disnake.Embed(
            title=title,
            description=f"{option_names}"
        )
        comps.append(disnake.ui.Button(label=f"Rescind", style=disnake.ButtonStyle.gray, custom_id=f"{inter.author.id}~pollrescind~{poll_id}"))
        comps.append(disnake.ui.Button(label=f"Delete", style=disnake.ButtonStyle.red, custom_id=f"{inter.author.id}~polldelete~{poll_id}"))
        embed.set_footer(text=f"A poll has been started by {inter.author}! Please press a button to vote.")
        embed.set_author(name=inter.author, icon_url=inter.author.display_avatar.url)
        await inter.response.send_message(embed=embed, components=comps, allowed_mentions=disnake.AllowedMentions.none())
    
    # @commands.slash_command(
    #     name="memberlist",
    #     description="Returns a list of server members.",
    #     guild_only=True,
    # )
    # async def memberlist(self, inter: disnake.ApplicationCommandInteraction):
    #     member_list = [member for member in inter.guild.members]
    #     member_list_str = ""
    #     bot_count = 0
    #     for member in member_list:
    #         if not member.bot:
    #             member_list_str += f"{member.mention}, "
    #         else:
    #             bot_count += 1
    #     member_list_str = member_list_str[:-2]
    #     await inter.response.send_message(content=f"Members**({len(member_list)-bot_count})**: {member_list_str}",allowed_mentions=disnake.AllowedMentions.none())

    # @commands.slash_command(
    #     name="commonuser",
    #     description="Returns all users that have spoken in recent messages.",
    #     default_member_permissions=disnake.Permissions(read_message_history=True),
    # )
    # async def commonuser(self, inter: disnake.ApplicationCommandInteraction, message_limit: int):
    #     user_dict = {}
    #     message_limit = min(message_limit, 1000)
    #     await inter.response.defer()
    #     async for msg in inter.channel.history(limit=message_limit+1):
    #         if not msg.author.bot:
    #             if msg.author in user_dict:
    #                 user_dict[msg.author] += 1
    #             else:
    #                 user_dict[msg.author] = 1
    #     output = ""
    #     for idx,user in enumerate(sorted(user_dict, key=user_dict.get, reverse=True)):
    #         if idx > 9:
    #             break
    #         output += f"{idx+1}. {user.mention} – **{user_dict[user]}** messages\n"
    #     embed = disnake.Embed(
    #         description=output,
    #         title=f"Most Common Users",
    #         colour=0xF0C43F,
    #     )
    #     embed.set_footer(text=f"Data retrieved in {round(inter.bot.latency * 1000)}ms")
    #     await inter.edit_original_message(embed=embed, allowed_mentions=disnake.AllowedMentions.none())
    
    # @commands.slash_command(
    #     name="commonword",
    #     description="Returns the most common word for users that have spoken in recent messages.",
    #     default_member_permissions=disnake.Permissions(read_message_history=True),
    # )
    # async def commonword(self, inter: disnake.ApplicationCommandInteraction, message_limit: int, depth: int = 1):
    #     now = datetime.now()
    #     current_time = now.strftime("%H:%M:%S")
    #     user_dict = {}
    #     depth = min(depth, 5)
    #     message_limit = min(message_limit, 1000)
    #     await inter.response.defer()
    #     async for msg in inter.channel.history(limit=message_limit+1):
    #         if not msg.author.bot:
    #             if msg.author in user_dict:
    #                 user_dict[msg.author] += msg.content.split()
    #             else:
    #                 user_dict[msg.author] = msg.content.split()
    #     output = ""
    #     for key in user_dict:
    #         data = Counter(user_dict[key])
    #         most_common_words = data.most_common()
    #         user_output = ""
    #         for idx in range(min(depth, len(most_common_words))):
    #             word = most_common_words[idx][0]
    #             count = most_common_words[idx][1]
    #             user_output += f"\"`{word}`\"({count} times), "
    #         user_output = user_output[:-2]
    #         output += f"{key.mention} – {user_output}\n"
    #     embed = disnake.Embed(
    #         description=output,
    #         title=f"Most Common Words Per User",
    #         colour=0x0000FF,
    #     )
    #     embed.set_footer(text=f"Data retrieved in {round(inter.bot.latency * 1000)}ms")
    #     await inter.edit_original_message(embed=embed, allowed_mentions=disnake.AllowedMentions.none())
    
    @commands.slash_command(
        name="userinfo",
        description="Gets info for a user on Discord.",
        guild_only=True
    )
    async def userinfo(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User = None):
        if user is None:
            user = inter.author
        embed = disnake.Embed(
            description=f"User Nickname: {user.name}\nUser Tag: {user}\nUser ID: {user.id}\n\n**\"{get_user_description(user.id)}\"**\n\nCreated At: {user.created_at}",
            colour=0xF0C43F
        )
        if inter.guild.get_member(user.id) in inter.guild.members:
            roles = user.roles
            highest_role = roles[-1].mention
            role_list = [r.mention for r in roles]
            role_list_str = ""
            for r in role_list:
                role_list_str += f"{r} "
            embed.description += f"\nHighest Role: {highest_role}\nRoles: {role_list_str}\nJoined Server On: {user.joined_at}"
        embed.set_author(name=user, icon_url=user.display_avatar.url)
        embed.set_thumbnail(user.avatar)
        embed.set_footer(text=f"Data retrieved in {round(inter.bot.latency * 1000)}ms | Information requested by {inter.author}")
        await inter.send(embed=embed)
    
    @commands.slash_command(
        name="setdescription",
        description="Sets your description on your profile. (max. 500 charcaters)",
    )
    async def setdescription(self, inter: disnake.ApplicationCommandInteraction, description: str):
        if len(description) > 200:
            await inter.response.send_message(content="Too long! (max. 200 characters)", ephemeral=True)
            return
        set_user_description(inter.author.id, description)
        embed = disnake.Embed(
            description=f"Description successfully set to:\n\n{description}"
        )
        await inter.response.send_message(embed=embed, ephemeral=True)
        
    @commands.slash_command(
        name="purge",
        description="Deletes an amount of messages(max: 100).",
        default_member_permissions=disnake.Permissions(manage_messages=True),
        guild_only=True,
    )
    async def purge(self, inter: disnake.ApplicationCommandInteraction, amount: int):
        amount = min(amount, 100)
        await inter.response.defer()
        await inter.send(content=f"Attempting to delete {amount} messages...", ephemeral=True)
        await inter.channel.purge(limit=amount+1)
        
    @commands.slash_command(
        name="help",
        description="Returns a list of commands."
    )
    async def help(self, inter: disnake.ApplicationCommandInteraction):
        cmds=inter.bot.global_slash_commands
        max_help_pages = int((len(cmds) / 9) + 1)
        comps = [
                disnake.ui.Button(label="◀", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~helpback~1"),
                disnake.ui.Button(label="▶", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~helpforward~1"),
                disnake.ui.Button(label="Exit", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~helpexit~1")
            ]
        embed = disnake.Embed(
            title=f"Commands List Page 1 of {max_help_pages}",
            )
        for cmd in itertools.islice(cmds, 0, min(9, len(cmds))):
            embed.add_field(
                name=f"/{cmd.name}",
                value=cmd.description
            )
        await inter.send(embed=embed,components=comps)
        
    @commands.Cog.listener()
    async def on_button_click(self, inter: disnake.MessageInteraction):
        id_parts = inter.component.custom_id.split('~')
        button_id = id_parts[1]
        
        max_help_pages = int((len(inter.bot.global_slash_commands) / 9) + 1)
        if button_id == "helpback":
            author_id = int(id_parts[0])
            if inter.author.id == author_id:
                
                help_page = int(id_parts[2])
                if help_page > 1:
                    help_page -= 1
                    cmds=inter.bot.global_slash_commands
                    embed = disnake.Embed(
                        title=f"Commands List Page {(help_page)} of {max_help_pages}",
                        )
                    for cmd in itertools.islice(cmds, (help_page-1) * 9, min(help_page * 9, len(cmds))):
                        embed.add_field(
                        name=f"/{cmd.name}",
                        value=cmd.description
                    )
                    comps = [
                        disnake.ui.Button(label="◀", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~helpback~{help_page}"),
                        disnake.ui.Button(label="▶", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~helpforward~{help_page}"),
                        disnake.ui.Button(label="Exit", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~helpexit~{help_page}")
                    ]
                    await inter.response.defer()
                    await inter.edit_original_message(embed=embed, components=comps)
        if button_id == "helpforward":
            author_id = int(id_parts[0])
            if inter.author.id == author_id:
                help_page = int(id_parts[2])
                if help_page < max_help_pages:
                    help_page += 1
                    cmds=inter.bot.global_slash_commands
                    embed = disnake.Embed(
                        title=f"Commands List Page {(help_page)} of {max_help_pages}",
                        )
                    for cmd in itertools.islice(cmds, (help_page-1) * 9, min(help_page * 9, len(cmds))):
                        embed.add_field(
                        name=f"/{cmd.name}",
                        value=cmd.description
                    )
                    comps = [
                        disnake.ui.Button(label="◀", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~helpback~{help_page}"),
                        disnake.ui.Button(label="▶", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~helpforward~{help_page}"),
                        disnake.ui.Button(label="Exit", style=disnake.ButtonStyle.blurple, custom_id=f"{inter.author.id}~helpexit~{help_page}")
                    ]
                    await inter.response.defer()

                    await inter.edit_original_message(embed=embed, components=comps)
        if button_id == "helpexit":
            author_id = int(id_parts[0])
            if inter.author.id == author_id:
                await inter.response.defer()
                await inter.delete_original_message()
        if button_id == "pollvote":
            poll_id = id_parts[2]
            option_id = id_parts[3]
            remove_vote(poll_id, inter.author.id)
            add_vote(poll_id, option_id, inter.author.id)
            await inter.response.defer()
            
            message = await inter.original_message()
            embed = message.embeds[0]
            description = ""
            options = get_options(poll_id)
            for option in options:
                votes = get_votes(option)
                description += f"{options[option]}: {votes}\n"
            embed.description = description
            await inter.edit_original_message(embed=embed)
        if button_id == "pollrescind":
            poll_id = id_parts[2]
            remove_vote(poll_id, inter.author.id)
            await inter.response.defer()
            
            message = await inter.original_message()
            embed = message.embeds[0]
            description = ""
            options = get_options(poll_id)
            for option in options:
                votes = get_votes(option)
                description += f"{options[option]}: {votes}\n"
            embed.description = description
            await inter.edit_original_message(embed=embed)
        if button_id == "polldelete":
            author_id = int(id_parts[0])
            if inter.author.id == author_id:
                await inter.response.defer()
                await inter.delete_original_message()

def setup(bot: commands.Bot):
    bot.add_cog(UtilCommand(bot))