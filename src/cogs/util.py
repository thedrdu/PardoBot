from distutils.command.config import config
from typing import Counter
import disnake
import io
import aiohttp
import asyncio
import collections
import itertools
from disnake.ext import commands, tasks
from datetime import datetime, timedelta
from data.general_util import set_reminder, get_reminder, create_poll, insert_option, remove_vote, add_vote, get_options, get_votes, get_user_description, set_user_description


class UtilCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.check.start()
    
    @tasks.loop(seconds=60.0)
    async def check(self):
        print("Checking for reminders...")
        data = get_reminder()
        reminders = data[0]
        creation_times = data[1]
        for user_id in reminders:
            print(f"reminder for {user_id}")
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
    
    @commands.slash_command(
        name="memberlist",
        description="Returns a list of server members.",
        guild_only=True,
        # guild_ids=[1234, 5678]
    )
    async def memberlist(self, inter: disnake.ApplicationCommandInteraction):
        member_list = [member for member in inter.guild.members]
        member_list_str = ""
        bot_count = 0
        for member in member_list:
            if not member.bot:
                member_list_str += f"{member.mention}, "
            else:
                bot_count += 1
        member_list_str = member_list_str[:-2]
        await inter.response.send_message(content=f"Members**({len(member_list)-bot_count})**: {member_list_str}",allowed_mentions=disnake.AllowedMentions.none())
    
    
    @commands.slash_command(
        name="botlist",
        description="Returns a list of server bots.",
        guild_only=True,
        # guild_ids=[1234, 5678]
    )
    async def botlist(self, inter: disnake.ApplicationCommandInteraction):
        emoji = "<:PardoPOG:992554480681889813>"
        bot_list = []
        for member in inter.guild.members:
            if member.bot and member.id != 975574636085530675:
                bot_list.append(member)
        output = ""
        for bot in bot_list:
            output += bot.mention + ", "
        output = output[:-2]
        await inter.response.send_message(f"Nya! {emoji} My fellow bots are: {output}")


    @commands.slash_command(
        name="commonuser",
        description="Returns all users that have spoken in recent messages."
    )
    async def commonuser(self, inter: disnake.ApplicationCommandInteraction, message_limit: int):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        user_dict = {}
        message_limit = min(message_limit, 1000)
        await inter.response.defer()
        async for msg in inter.channel.history(limit=message_limit+1):
            if not msg.author.bot:
                if msg.author in user_dict:
                    user_dict[msg.author] += 1
                else:
                    user_dict[msg.author] = 1
        output = ""
        for idx,user in enumerate(sorted(user_dict, key=user_dict.get, reverse=True)):
            if idx > 9:
                break
            output += f"{idx+1}. {user.mention} – **{user_dict[user]}** messages\n"
        embed = disnake.Embed(
            description=output,
            title=f"Most Common Users",
            colour=0xF0C43F,
        )
        embed.set_footer(text=f"Data retrieved from past {message_limit} messages at {current_time}")
        await inter.edit_original_message(embed=embed, allowed_mentions=disnake.AllowedMentions.none())
    
    @commands.slash_command(
        name="commonword",
        description="Returns the most common word for users that have spoken in recent messages.",
        default_member_permissions=disnake.Permissions(read_message_history=True),
    )
    async def commonword(self, inter: disnake.ApplicationCommandInteraction, message_limit: int, depth: int):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        user_dict = {}
        depth = min(depth, 5)
        message_limit = min(message_limit, 1000)
        await inter.response.defer()
        async for msg in inter.channel.history(limit=message_limit+1):
            if not msg.author.bot:
                if msg.author in user_dict:
                    user_dict[msg.author] += msg.content.split()
                else:
                    user_dict[msg.author] = msg.content.split()
        output = ""
        for key in user_dict:
            data = Counter(user_dict[key])
            most_common_words = data.most_common()
            user_output = ""
            for idx in range(min(depth, len(most_common_words))):
                word = most_common_words[idx][0]
                count = most_common_words[idx][1]
                user_output += f"\"`{word}`\"({count} times), "
            user_output = user_output[:-2]
            output += f"{key.mention} – {user_output}\n"
        embed = disnake.Embed(
            description=output,
            title=f"Most Common Words Per User",
            colour=0xF0C43F,
        )
        embed.set_footer(text=f"Data retrieved from past {message_limit} messages at {current_time} EST")
        await inter.edit_original_message(embed=embed, allowed_mentions=disnake.AllowedMentions.none())
            
    
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
        description="Sets your description on your profile.",
    )
    async def setdescription(self, inter: disnake.ApplicationCommandInteraction, description: str):
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
        deleted = await inter.channel.purge(limit=amount+1)
        
        
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
        global polls
        global creators
        id_parts = inter.component.custom_id.split('~')
        
        button_id = id_parts[1]
        
        max_help_pages = int((len(inter.bot.global_slash_commands) / 9) + 1)
        if button_id == "helpback":
            print("helpback")
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
            print("helpforward")
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