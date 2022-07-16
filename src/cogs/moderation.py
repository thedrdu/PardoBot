from distutils.command.config import config
import disnake
import asyncio
from disnake.ext import commands

modroles = {} #guild ID : mod role ID

class ModerationCommand(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        
    # @commands.slash_command(
    #     name="mute",
    #     description="Mutes a user in the server.",
    #     default_member_permissions=disnake.Permissions(manage_roles=True),
    #     guild_only=True,
    # )
    # async def mute(inter: disnake.ApplicationCommandInteraction, member: disnake.Member):
    #     muted_role = None
    #     for role in inter.guild.roles:
    #         if role.name == "Muted":     #Have to config with proper role ID in case of duplicate "Muted" roles
    #             muted_role = role
    #     if muted_role is None:
    #         inter.response.send_message(content=f"Muted role not found!", ephemeral=True)
    #         return
    #     member.add_roles()
    
    # @commands.slash_command(
    #     name="modrole",
    #     description="Config: Set selected role for Moderator command eligibility.",
    #     default_member_permissions=disnake.Permission(administrator=True),
    #     guild_only=True,
    # )
    # async def modrole(inter: disnake.ApplicationCommandInteraction, role: disnake.Role):
    #     modroles[inter.guild.id] = role.id
    
    @commands.slash_command(
        name="pardokick",
        description="Kicks a user from the guild.",
        default_member_permissions=disnake.Permissions(kick_members=True),
        guild_only=True,
    )
    async def pardokick(inter: disnake.ApplicationCommandInteraction, user: disnake.User, *, reason):
        await inter.send(content=f"Attempting to kick {user}...", ephemeral=True)
        await user.send(f"You have been kicked from {inter.guild.name} for: \"{reason}\"")
        await inter.guild.kick(user)
        await inter.edit_original_message(content=f"{user} successfully kicked!")
    
            
    @commands.slash_command(
        name="pardoban",
        description="Bans a user from the guild.",
        default_member_permissions=disnake.Permissions(ban_members=True),
        guild_only=True,
        # guild_ids=[1234, 5678]
    )
    async def pardoban(inter: disnake.ApplicationCommandInteraction, user: disnake.User, *, reason, appeal_contact: disnake.User = None):
        await inter.send(content=f"Attempting to ban {user}...", ephemeral=True)
        msg = f"You have been banned from {inter.guild.name} for: \"{reason}\"."
        if appeal_contact is not None:
            msg += f"\n\nContact **{appeal_contact}** to appeal."
        try:
            await user.send(msg)
        except:
            pass
        await inter.guild.ban(user)
        await inter.edit_original_message(content=f"{user} successfully banned!")
        
    
    @commands.slash_command(
        name="unban",
        description="Unbans a user from the server.",
        default_member_permissions=disnake.Permissions(ban_members=True),
        guild_only=True,
        # guild_ids=[1234, 5678]
    )
    async def unban(inter: disnake.ApplicationCommandInteraction, user: disnake.User):
        user = await inter.bot.fetch_user(user.id)
        await inter.send(content=f"Attempting to unban {user}...", ephemeral=True)
        await inter.guild.unban(user)
        await inter.edit_original_message(content=f"{user} successfully unbanned!")
        
    
    # @commands.slash_command(
    #     name="modflex",
    #     description="Flex your moderator priviliges.",
    #     default_member_permissions=()
    #     guild_only=True,
    #     # guild_ids=[1234, 5678]
    # )
        
def setup(bot: commands.Bot):
    bot.add_cog(ModerationCommand(bot))