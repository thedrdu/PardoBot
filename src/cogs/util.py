import disnake
from google_images_search import GoogleImagesSearch
import fandom, tweepy, json, requests, genshin
import os, io, aiohttp, asyncio, itertools
import google_auth_oauthlib.flow, googleapiclient.discovery, googleapiclient.errors
from disnake.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from data.general_util import set_reminder, get_reminder, create_poll, insert_option, remove_vote, add_vote, get_options, get_votes
from data.general_util import get_user_description, set_user_description
from data.general_util import set_honkai_user_info, get_honkai_user_info
from data.general_util import check_video_id, add_video_id, check_tweet_id, add_tweet_id
from data.general_util import update_news_guild, remove_news_guild, get_news_guilds
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
twt_username='HonkaiImpact3rd'

channel_id="UCko6H6LokKM__B03i5_vBQQ"
uploads_id="UUko6H6LokKM__B03i5_vBQQ"

def get_latest_video():
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2CcontentDetails&maxResults=1&playlistId={uploads_id}&key={GCS_DEVELOPER_KEY}"
    # url = f"https://www.googleapis.com/youtube/v3/search?key={GCS_DEVELOPER_KEY}&channelId={channel_id}&part=snippet,id&order=date&maxResults=1"
    json_url = requests.get(url)
    data = json.loads(json_url.text)
    # print(data)
    video_id = data['items'][0]['snippet']['resourceId']['videoId']
    return video_id

def get_latest_tweet():
    tweets_list = api.user_timeline(screen_name=twt_username, count=1)
    tweet = tweets_list[0]
    # print(tweet.user.profile_image_url_https)
    return tweet.id

class UtilCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reminder_check.start()
        self.social_check.start()
    
    @tasks.loop(seconds=60.0)
    async def social_check(self):
        tweet_id = get_latest_tweet()
        if check_tweet_id(tweet_id) is None:
            add_tweet_id(tweet_id)
            guild_channels = get_news_guilds()
            for guild_id in guild_channels.keys():
                guild = await self.bot.fetch_guild(guild_id)
                channel = await self.bot.fetch_channel(guild_channels[guild_id])
                await channel.send(content=f"<:Pardofelis_Icon:1000849934343491695>Meow! A new tweet from <:AI_Chan_Icon:1001125788189470831>Ai-Chan has arrived!\n\n https://twitter.com/{twt_username}/status/{tweet_id}")
        video_id = get_latest_video()
        if check_video_id(video_id) is None:
            add_video_id(video_id)
            guild_channels = get_news_guilds()
            for guild_id in guild_channels.keys():
                guild = await self.bot.fetch_guild(guild_id)
                channel = await self.bot.fetch_channel(guild_channels[guild_id])
                await channel.send(content=f"<:Pardofelis_Icon:1000849934343491695>Meow! A new video from <:AI_Chan_Icon:1001125788189470831>Ai-Chan has arrived!\n\n https://www.youtube.com/watch?v={video_id}")
        
    @tasks.loop(seconds=60.0)
    async def reminder_check(self):
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
        name="latesttweet",
        description="Returns the latest tweet from the official HI3 Twitter account."
    )
    async def latesttweet(self, inter: disnake.ApplicationCommandInteraction):
        tweet_id = get_latest_tweet()
        await inter.response.send_message(content=f"https://twitter.com/HonkaiImpact3rd/status/{tweet_id}")
    
    # @commands.slash_command(
    #     name="latestvideo",
    #     description="Returns the latest video from the official HI3 YouTube channel."
    # )
    # async def latestvideo(self, inter: disnake.ApplicationCommandInteraction):
    #     video_id = get_latest_video()
    #     await inter.response.send_message(content=f"https://www.youtube.com/watch?v={video_id}")
    
    @commands.slash_command(
        name="configstats",
        description="Configure user HoYoLAB profile on PardoBot.",
    )
    async def configstats(self, inter: disnake.ApplicationCommandInteraction, ltuid: int, ltoken: str, honkai_uid: int):
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
    async def remindme(self, inter: disnake.ApplicationCommandInteraction, reminder: str, days: int = 0, hours: int = 0, minutes: int = 1):
        reminder_time = datetime.now().astimezone(timezone.utc) + timedelta(days=days, hours=hours, minutes=minutes)
        set_reminder(inter.author.id, reminder, reminder_time.strftime("%Y:%m:%d:%H:%M"), datetime.now().strftime("%Y:%m:%d:%H:%M"))
        await inter.response.send_message(content=f"Reminder successfully set!", ephemeral=True)
        
    @commands.slash_command(
        name="avatar",
        description="Returns the target user's avatar.",
    )
    async def avatar(self, inter: disnake.ApplicationCommandInteraction, user: disnake.User):
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
    
    
    @commands.slash_command(
        name="userinfo",
        description="Retrieves the target user's information.",
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
        
        booster_ids = [booster.id for booster in inter.guild.premium_subscribers]
        if user.id in booster_ids:
            embed.color = 0xF47FFF
        await inter.send(embed=embed)
    
    @commands.slash_command(
        name="setdescription",
        description="Sets user description on profile. (max. 200 characters)",
    )
    async def setdescription(self, inter: disnake.ApplicationCommandInteraction, description: str):
        if len(description) > 200:
            await inter.response.send_message(content="Too long! (max. 200 characters)", ephemeral=True)
        else:
            set_user_description(inter.author.id, description)
            embed = disnake.Embed(
                description=f"Description successfully set to:\n\n{description}"
            )
            await inter.response.send_message(embed=embed, ephemeral=True)
        
    @commands.slash_command(
        name="purge",
        description="Deletes messages from the current channel (max. 500 messages).",
        default_member_permissions=disnake.Permissions(manage_messages=True),
        guild_only=True,
    )
    async def purge(self, inter: disnake.ApplicationCommandInteraction, amount: int):
        amount = min(amount, 500)
        await inter.response.defer()
        await inter.send(content=f"Attempting to delete {amount} messages...", ephemeral=True)
        await inter.channel.purge(limit=amount+1)
        
    @commands.slash_command(
        name="confignews",
        description="Configure the server's Honkai Impact 3rd news channel.",
        guild_only=True,
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def confignews(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel):
        update_news_guild(inter.guild.id, channel.id)
        await inter.response.send_message(content=f"Updated {inter.guild.name} to receive updates in {channel.mention}.", ephemeral=True)
        
    @commands.slash_command(
        name="resetconfignews",
        description="Reset the server's Honkai Impact 3rd news channel.",
        guild_only=True,
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def resetconfignews(self, inter: disnake.ApplicationCommandInteraction):
        if remove_news_guild(inter.guild.id) is None:
            await inter.response.send_message(content="No Honkai Impact 3rd news channel has been configured yet!", ephemeral=True)
        else:
            await inter.response.send_message(content=f"Removed Honkai Impact 3rd news channel from {inter.guild.name}.", ephemeral=True)
        
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
    async def on_member_join(self, inter: disnake.Member):
        #Have to config this to be a unique channel for each server
        channel = self.bot.get_channel(1000906850226667630)
        embed = disnake.Embed(
            title=f"Welcome new captain!",
            description=f"<:Pardofelis_Icon:1000849934343491695> {inter.mention} has boarded the Hyperion!",
            color=0x7DA565
        )
        embed.set_thumbnail(url=inter.avatar.url)
        current_time = datetime.now().astimezone(timezone.utc).strftime("%H:%M:%S")
        embed.set_footer(text=f"{current_time} UTC",icon_url=self.bot.user.avatar.url)
        await channel.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_member_remove(self, inter: disnake.Member):
        channel = self.bot.get_channel(1000906850226667630)
        embed = disnake.Embed(
            title=f"Goodbye, captain...",
            description=f"<:Pardofelis_Icon:1000849934343491695> {inter.mention} has departed the Hyperion...",
            color=0xFF0000
        )
        embed.set_thumbnail(url=inter.avatar.url)
        current_time = datetime.now().astimezone(timezone.utc).strftime("%H:%M:%S")
        embed.set_footer(text=f"{current_time} UTC",icon_url=self.bot.user.avatar.url)
        await channel.send(embed=embed)
    
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