import disnake
import fandom, tweepy, json, requests, genshin
import os, io, aiohttp, asyncio, itertools
from disnake.ext import commands, tasks
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from data.general_util import set_reminder, get_reminder, create_poll, insert_option, remove_vote, add_vote, get_options, get_votes, set_user_description, get_user_description

class UtilCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.reminder_check.start()
    
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