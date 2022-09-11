import disnake
from google_images_search import GoogleImagesSearch
import fandom, tweepy, json, requests, genshin
import os, io, aiohttp, asyncio, itertools
import google_auth_oauthlib.flow, googleapiclient.discovery, googleapiclient.errors
from disnake.ext import commands, tasks
from dotenv import load_dotenv
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
    video_id = data['items'][0]['snippet']['resourceId']['videoId']
    return video_id

def get_latest_tweet():
    tweets_list = api.user_timeline(screen_name=twt_username, count=1)
    tweet = tweets_list[0]
    return tweet.id

class HonkaiCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.social_check.start()
    
    @tasks.loop(seconds=60.0)
    async def social_check(self):
        tweet_id = get_latest_tweet()
        if check_tweet_id(tweet_id) is None:
            add_tweet_id(tweet_id)
            guild_channels = get_news_guilds()
            for guild_id in guild_channels.keys():
                try:
                    channel = await self.bot.fetch_channel(guild_channels[guild_id])
                except:
                    remove_news_guild(guild_id)
                await channel.send(content=f"<:Pardofelis_Icon:1000849934343491695>Meow! A new tweet from <:AI_Chan_Icon:1001125788189470831>Ai-Chan has arrived!\nhttps://twitter.com/{twt_username}/status/{tweet_id}")
        video_id = get_latest_video()
        if check_video_id(video_id) is None:
            add_video_id(video_id)
            guild_channels = get_news_guilds()
            for guild_id in guild_channels.keys():
                try:
                    channel = await self.bot.fetch_channel(guild_channels[guild_id])
                except:
                    remove_news_guild(guild_id)
                await channel.send(content=f"<:Pardofelis_Icon:1000849934343491695>Meow! A new video from <:AI_Chan_Icon:1001125788189470831>Ai-Chan has arrived!\nhttps://www.youtube.com/watch?v={video_id}")

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
        description="Configure user HoYoLAB profile on PardoBot. Type carefully!",
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
        else:
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
        name="confignews",
        description="Configure the server's Honkai Impact 3rd news channel.",
        guild_only=True,
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def confignews(self, inter: disnake.ApplicationCommandInteraction, channel: disnake.TextChannel):
        try:
            embed = disnake.Embed(
                title=f"Honkai Impact 3rd News Updates",
                description=f"{channel.mention} successfully configured to receive Honkai Impact 3rd news updates!"
            )
            await channel.send(embed=embed)
        except disnake.Forbidden:
            await inter.response.send_message(content=f"PardoBot does not have permission to send messages to {channel.mention}!", ephemeral=True)
        else:
            update_news_guild(inter.guild.id, channel.id)
            await inter.response.send_message(content=f"Updated {inter.guild.name} to receive updates in {channel.mention}.", ephemeral=True)
        
    @commands.slash_command(
        name="resetnews",
        description="Reset the server's Honkai Impact 3rd news channel.",
        guild_only=True,
        default_member_permissions=disnake.Permissions(administrator=True),
    )
    async def resetnews(self, inter: disnake.ApplicationCommandInteraction):
        if remove_news_guild(inter.guild.id) is None:
            await inter.response.send_message(content="No Honkai Impact 3rd news channel has been configured yet!", ephemeral=True)
        else:
            await inter.response.send_message(content=f"Removed Honkai Impact 3rd news channel from {inter.guild.name}.", ephemeral=True)

def setup(bot: commands.Bot):
    bot.add_cog(HonkaiCommand(bot))