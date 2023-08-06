import discord
from discord.ext import commands
import aiosqlite
from datetime import timedelta
from discord import Color
from discord import app_commands
from datetime import datetime
from discord.ext.commands import CommandNotFound, CommandOnCooldown, MissingPermissions, MissingRequiredArgument, has_permissions

from discord.app_commands import AppCommandError


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


####################################################################################################################################
#################################################################################################################################### BAN START
####################################################################################################################################

    @app_commands.command(
        name="ban",
        description="Bans the passed user.",
    )
    @app_commands.default_permissions(ban_members=True)
    @app_commands.describe(member='The member to ban.', reason='The reason for the ban.', private='If the ban message should be private.')
    async def ban(
        self, interaction: discord.Interaction, member: discord.User, reason: str = None, private:bool=False
   ):
        
        print("[Ban] has just been executed")
        await interaction.response.defer(ephemeral=private, thinking=True)



        db = await aiosqlite.connect("config.db")

        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )
        cur = await db.execute(
            f"""SELECT * FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        row = await cur.fetchone()
        if row is None:
            await interaction.followup.send(f'To setup {self.bot.user}\'s commands properly, run /help and choose the setup section')
            return

        res = await cur.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0]

        
        if interaction.user.top_role > member.top_role:

            if not member.bot:
                embed = discord.Embed(
                    title="**Banned**",
                    description=f'**You were banned from "{interaction.guild.name}"**\n> Reason: "{reason}"\n> Responsible: {interaction.user.mention}',
                    timestamp=datetime.utcnow(),
                    color=Color.red(),
                )
                embed.set_footer(text="Border hopping hispanic")

            await member.send(
                embed=embed
            )

            await interaction.guild.ban(member, reason=reason)
            await interaction.followup.send(embed=discord.Embed(
                title=f'**Ban**',
                description=f'> Banned: {member.mention}\n> Reason: "{reason}"',color=Color.red()),
            )

            embed2 = discord.Embed(
                title="! **• BAN •** !",
                description=f"- 🧍 Issuer: {interaction.user.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n- 🖊️ Reason: {reason}",
                timestamp=datetime.utcnow(),
                color=Color.from_rgb(27, 152, 250),
            )

            embed2.set_footer(text="Border hopping hispanic")

            channel = self.bot.get_channel(logs)


            await channel.send(
                embed=embed2.set_thumbnail(url=interaction.user.avatar.url)
                )
        else:
            await interaction.followup.send(
                f"{interaction.user.mention}, {member.mention} has higher perms than you.",
                ephemeral=True,
            )
         

    @ban.error
    async def on_ban_error(
        self, interaction: discord.Interaction, error: AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(content=str(error), ephemeral=True)

    @app_commands.command(name='unban', description="Unbans the passed user.")
    @app_commands.default_permissions(ban_members=True, manage_roles=True)
    @app_commands.describe(member='The member to unban.', private='If the unban message should be private.')
    async def unban(self, interaction: discord.Interaction, member: discord.User, private:bool=False):
            print("[Unban] has just been executed")
            await interaction.response.defer(ephemeral=private,thinking=True)

            db = await aiosqlite.connect("config.db")

            await db.execute(
                """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
            )
            cur = await db.execute(
                f"""SELECT * FROM logs WHERE guild_id = {interaction.guild.id}"""
            )
            row = await cur.fetchone()
            if row is None:
                await interaction.followup.send(f'To setup {self.bot.user}\'s commands properly, run /help and choose the setup section')
                return

            res = await cur.execute(
                f"""SELECT channel_id FROM logs WHERE guild_id = {interaction.guild.id}"""
            )
            channel = await res.fetchone()
            logs = channel[0]

            await interaction.guild.unban(member)
            await interaction.followup.send(embed=discord.Embed(
                title='**Unban**',
                description=f"> Unbanned: {member.mention}",color=Color.green()),
            )
            embed2 = discord.Embed(
                title="! **• UNBAN •** !",
                description=f"- 🧍 Issuer: {interaction.user.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`",
                timestamp=datetime.utcnow(),
                color=Color.from_rgb(27, 152, 250),
            )

            embed2.set_footer(text="Border hopping hispanic")
            channel = self.bot.get_channel(logs)

            if logs is not None:
                await channel.send(
                    embed=embed2.set_thumbnail(url=interaction.user.avatar.url)
                )

    @unban.error
    async def on_unban_error(
        self, interaction: discord.Interaction, error: AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(embed=discord.Embed(title='**Cooldown**',description=str(error), color=Color.red()), ephemeral=True)
        if isinstance(error, commands.UnknownBan):
            await interaction.response.send_message(embed=discord.Embed(title='**Ban error**', description=f'> The passed member is not banned', color=Color.red()), ephemeral=True)

####################################################################################################################################
#################################################################################################################################### BAN END, MUTE START
####################################################################################################################################


    @app_commands.command(name="mute", description="Tempmutes the passed user.")
    @app_commands.default_permissions(mute_members=True)
    @app_commands.describe(member='The member to mute.', minutes='The amount of minutes to mute the member for.', hours='The amount of hours to mute the member for.', days='The amount of days to mute the member for.', reason='The reason for the mute.', private='If the mute message should be private.')
    async def mute(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: int = 10,
        hours: int = 0,
        days: int = 0,
        reason: str = None,
        private:bool=False,
    ) -> None:
        print("[Mute] has just been executed")
        await interaction.response.defer(ephemeral=private, thinking=True)

        db = await aiosqlite.connect("config.db")

        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )
        cur = await db.execute(
            f"""SELECT * FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        row = await cur.fetchone()
        if row is None:
            await interaction.followup.send(f'To setup {self.bot.user}\'s commands properly, run /help and choose the setup section')
            return

        res = await cur.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        channel = await res.fetchone()

        logs = channel[0]

        if member.top_role.permissions.administrator == False:
            guild = interaction.guild

            if member.is_timed_out() == False:
                delta = timedelta(minutes=minutes, hours=hours, days=days)

                await member.timeout(delta, reason=reason)
                await interaction.followup.send(embed=discord.Embed(
                    title='**Mute**',
                    description=f'> Muted: {member.mention}\n> Reason: "{reason}"',color=Color.red()),
                )

                embed = discord.Embed(
                    title="**Muted**",
                    description=f'**You were muted in "{interaction.guild.name}"**\n> Reason: `{reason}`\n> Responsible: {interaction.user.mention}\n> Duration: {minutes}m, {hours}h, {days}d',
                    timestamp=datetime.utcnow(),
                    color=Color.red(),
                )
                embed.set_footer(text="Border hopping hispanic")

                await member.send(
                    embed=embed,
                )

                embed2 = discord.Embed(
                    title="! **• MUTE •** !",
                    description=f"- 🧍 Issuer: {interaction.user.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n- 🖊️ Reason: {reason}",
                    timestamp=datetime.utcnow(),
                    color=Color.from_rgb(27, 152, 250),
                )

                await member.move_to(None)

                if logs is not None:
                    channel = self.bot.get_channel(logs)

                    await channel.send(
                        embed=embed2.set_thumbnail(url=interaction.user.avatar.url)
                    )

            else:
                await interaction.followup.send(
                    f"{interaction.user.mention}, {member.mention} is already muted!",
                    ephemeral=True,
                )

        else:
            await interaction.followup.send(
                f"{interaction.user.mention}, {member.mention} is staff!",
                ephemeral=True,
            )

    @app_commands.command(
        name="unmute", description="Unmutes the passed user."
    )
    @app_commands.default_permissions(mute_members=True)
    @app_commands.describe(member='The member to unmute.', private='If the unmute message should be private.')
    async def unmute(self, interaction: discord.Interaction, member: discord.Member, private:bool=False):
        print("[Unmute] has just been executed")
        await interaction.response.defer(ephemeral=private,thinking=True)

        db = await aiosqlite.connect("config.db")

        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )
        cur = await db.execute(
            f"""SELECT * FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        row = await cur.fetchone()
        if row is None:
            await interaction.followup.send(f'To setup {self.bot.user}\'s commands properly, run /help and choose the setup section')
            return

        res = await cur.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0]

        if member.is_timed_out() == True:
            await member.timeout(None)

            
            await interaction.followup.send(embed=discord.Embed(
                title='**Unmute**',
                description=f"> Unmuted: {member.mention}",color=Color.green()),
            )

            embed = discord.Embed(
                title="! **• UNMUTE •** !",
                description=f"- 🧍 Issuer: {interaction.user.mention}\n-🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`",
                timestamp=datetime.utcnow(),
                color=Color.from_rgb(27, 152, 250),
            )

            embed.set_footer(text="Border hopping hispanic")
            channel = self.bot.get_channel(logs)

            embed2 = discord.Embed(
                title="**Unmuted**",
                timestamp=datetime.utcnow(),
                description=f'**You were unmuted in "{interaction.guild.name}"**\n> Responsible: {interaction.user}\n ',
                color=Color.green()
            )
            embed2.set_footer(text="Border hopping hispanic")

            await member.send(
                embed=embed2,
            )


            await channel.send(
                embed=embed.set_thumbnail(url=(interaction.user.avatar.url))
            )
        else:
            await interaction.followup.send(
                f"{interaction.user.mention}, {member} Is not muted.", ephemeral=True
            )

####################################################################################################################################
#################################################################################################################################### MUTE END, KICK START
####################################################################################################################################

    @app_commands.command(
        name="kick", description="Kicks the passed user."
    )
    @app_commands.default_permissions(kick_members=True)
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(member='The member to kick.', reason='The reason for the kick.', private='If the kick message should be visible for others.')
    async def kick(
        self, interaction: discord.Interaction, member: discord.Member, reason: str=None, private:bool=False
    ) -> None:
        print("[Kick] has just been executed")
        await interaction.response.defer(ephemeral=private,thinking=True)

        db = await aiosqlite.connect("config.db")

        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )
        cur = await db.execute(
            f"""SELECT * FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        row = await cur.fetchone()
        if row is None:
            await interaction.followup.send(f'To setup {self.bot.user}\'s commands properly, run /help and choose the setup section')
            return

        res = await cur.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0]

        if member.top_role.permissions.administrator == False:
            invite = await interaction.guild.text_channels[0].create_invite(
                    max_age=0, max_uses=1, unique=True
                )

            embed = discord.Embed(title='**Kicked**',
                description=f'**You were kicked from "{interaction.guild.name}"**\n> Reason: `{reason}`\n> Responsible: {interaction.user}\n> \n> [Rejoin {interaction.guild.name}]({invite})',
                timestamp=datetime.utcnow(),
                color=Color.red(),
            )
            embed.set_footer(text="Border hopping hispanic")

            await member.send(
                embed=embed,
            )
            await interaction.followup.send(embed=discord.Embed(
                title='**Kick**',
                description=f'> Kicked: {member.mention}\n> Reason: "{reason}"',color=Color.red()),
            )
            await member.kick(reason=reason)

            embed2 = discord.Embed(
                title="! **• KICK •** !",
                description=f"- 🧍 Issuer: {interaction.user.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n- 🖊️ Reason: {reason}",
                timestamp=datetime.utcnow(),
                color=Color.from_rgb(27, 152, 250),
            )

            embed2.set_footer(text="Border hopping hispanic")
            channel = self.bot.get_channel(logs)

            if logs is not None:
                await channel.send(
                    embed=embed2.set_thumbnail(url=interaction.user.avatar.url)
                )
        else:
            await interaction.response.send_message(
                f"{interaction.user.mention}, {member} is staff!", ephemeral=True
            )

    @kick.error
    async def on_kick_error(
        self, interaction: discord.Interaction, error: AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(content=str(error), ephemeral=True)

####################################################################################################################################
#################################################################################################################################### KICK END, CLEAR START
####################################################################################################################################

    @app_commands.command(name="clear", description="Clears messages from the passed user")
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(member='The member to clear messages from', amount='The range of messages to delete', private='If the clear message should be visible for others.')
    async def clear(
        self, interaction: discord.Interaction, member: discord.User, amount: int, private:bool=False
    ):
        print("[Clear] has just been executed")
        await interaction.response.defer(ephemeral=private, thinking=True)


        def check_author(m):
            return m.author.id == member.id
        

        await interaction.channel.purge(limit=amount, check=check_author)
        await interaction.followup.send(embed=discord.Embed(title='**Clear**', description=f'> Messages cleared: `{amount}`',color=Color.green()))

    @clear.error
    async def on_clear_error(
        self, interaction: discord.Interaction, error: AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(content=str(error), ephemeral=True)

####################################################################################################################################
#################################################################################################################################### CLEAR END, PURGE START
####################################################################################################################################

    @app_commands.command(
        name="purge", description="Deletes the passed amount of messages."
    )
    @app_commands.default_permissions(manage_messages=True)
    @app_commands.checks.cooldown(1, 15, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(amount='The amount of bulk messages to delete.', private='If the purge message should be visible for others.')
    async def purge(self, interaction: discord.Interaction, amount: int = 5, private:bool=False) -> None:
        print("[Purge] has just been executed!")
        await interaction.response.defer(ephemeral=private, thinking=True)

        floor = 2
        ceiling = 50
    
       
        if amount >= floor and amount <= ceiling:
            await interaction.channel.purge(limit=amount)
            await interaction.followup.send(embed=discord.Embed(
                title='**Purge**',
                description=f"> Deleted: {amount} messages", color=Color.green()))
           

        elif amount < floor:
            await interaction.followup.send(embed=discord.Embed(
                title='**Purge**',
                description=f"> Error: Amount is less than `{floor}`\n> Usage example: `/purge amount:5`",color=Color.red()),
            ephemeral=True)
            

        elif amount > ceiling:
            await interaction.followup.send(embed=discord.Embed(
                title='**Purge**',
                description=f"> Error: Amount must be less than `{ceiling}`\n> Usage example: `/purge amount:5`",color=Color.red()),
            ephemeral=True)

    @purge.error
    async def on_purge_error(
        self, interaction: discord.Interaction, error: AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(content=str(error), ephemeral=True)

####################################################################################################################################
#################################################################################################################################### PURGE END, BLACKLIST START
####################################################################################################################################

    @app_commands.command(
        name="blacklist", description="Blacklists the passed user."
    )
    @app_commands.default_permissions(mute_members=True)
    @app_commands.describe(member='The member to blacklist.', reason='The reason for the blacklist.', private='If the blacklist message should be visible for others.')
    async def blacklist(self, interaction: discord.Interaction, member: discord.Member, reason: str, private:bool=False) -> None:
        
        print("[Blacklist] has just been executed")
        await interaction.response.defer(ephemeral=private, thinking=True)


        db = await aiosqlite.connect("config.db")


        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )
        cur = await db.execute(
            f"""SELECT * FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        row = await cur.fetchone()
        if row is None:
            await interaction.followup.send(f'{interaction.user.mention}, To setup {self.bot.user}\'s commands properly, run /logs to set a commands log channel')
            return

        res = await cur.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0] 

        if member.top_role.permissions.administrator == False:

                print('Got past hierarchy checks') 
                cur = await db.execute(f"""SELECT banned_role_id FROM blacklist WHERE guild_id = ?""", (interaction.guild.id, ))
                roleid = await cur.fetchone()
                if roleid is None:
                    await interaction.followup.send(f'{interaction.user.mention}, to setup the blacklist command, run /setupblacklist')
                    return

                role = interaction.guild.get_role(roleid[0])
                if role not in member.roles:

                    await member.add_roles(role)
                    
                    await interaction.followup.send(embed=discord.Embed(
                        title='**Blacklist**',
                        description=f'> Blacklisted: {member.mention}\n> Reason: "{reason}"',color=Color.red()))

                    embed = discord.Embed(
                        title="**Blacklisted**",
                        description=f'**You have been blacklisted on "{interaction.guild.name}"**\n> Reason: `{reason}`\n> Responsible: {interaction.user}\n ',
                        timestamp=datetime.utcnow(),
                        color=Color.red(),
                    ).set_footer(text="Border hopping hispanic")

                    await member.send(
                        embed=embed)
                    
                    embed2 = discord.Embed(
                        title="**! • BLACKLIST • !**",
                        description=f"- 🧍 Issuer: {interaction.user.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n- 🖊️ Reason: {reason}",
                        timestamp=datetime.utcnow(),
                        color=Color.from_rgb(27, 152, 250),
                    ).set_footer(text="Border hopping hispanic")
                    await member.move_to(channel=None)

                    channel = self.bot.get_channel(logs)

                    if logs is not None: 
                        await channel.send(
                            embed=embed2.set_thumbnail(url=interaction.user.avatar.url))
                        
                else:
                    await interaction.followup.send(
                    f"{interaction.user.mention}, {member.mention} is already Blacklisted.",
                    ephemeral=True)

        else:
            await interaction.followup.send(
                f"{interaction.user.mention}, {member.mention} is staff!",
                ephemeral=True)

    @blacklist.error
    async def on_blacklist_error(
        self, interaction: discord.Interaction, error: AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.followup.send(content=str(error), ephemeral=True)
            

    @app_commands.command(
        name="blacklist", description="Blacklists the passed user."
    )
    @app_commands.default_permissions(mute_members=True)
    @app_commands.describe(member='The member to blacklist.', reason='The reason for the blacklist.', private='If the blacklist message should be private.')
    async def blacklist(self, interaction: discord.Interaction, member: discord.Member, reason: str, private:bool=False) -> None:
        
        print("[Blacklist] has just been executed")
        await interaction.response.defer(ephemeral=private, thinking=True)


        db = await aiosqlite.connect("config.db")


        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )
        cur = await db.execute(
            f"""SELECT * FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        row = await cur.fetchone()
        if row is None:
            await interaction.followup.send(f'{interaction.user.mention}, To setup {self.bot.user}\'s commands properly, run /logs to set a commands log channel')
            return

        res = await cur.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0] 

        if member.top_role.permissions.administrator == False:

                print('Got past hierarchy checks') 
                cur = await db.execute(f"""SELECT banned_role_id FROM blacklist WHERE guild_id = ?""", (interaction.guild.id, ))
                roleid = await cur.fetchone()
                if roleid is None:
                    await interaction.followup.send(f'{interaction.user.mention}, to setup the blacklist command, run /setupblacklist')
                    return

                role = interaction.guild.get_role(roleid[0])
                if role not in member.roles:

                    await member.add_roles(role)

                    
                    await interaction.followup.send(embed=discord.Embed(
                        title='**Blacklist**',
                        description=f'> Blacklisted: {member.mention}\n> Reason: "{reason}"',color=Color.red()))

                    embed = discord.Embed(
                        title="**Blacklisted**",
                        description=f'**You have been blacklisted on "{interaction.guild.name}"**\n> Reason: `{reason}`\n> Responsible: {interaction.user}\n ',
                        timestamp=datetime.utcnow(),
                        color=Color.red(),
                    ).set_footer(text="Border hopping hispanic")

                    await member.send(
                        embed=embed)
                    
                    embed2 = discord.Embed(
                        title="**! • BLACKLIST • !**",
                        description=f"- 🧍 Issuer: {interaction.user.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n- 🖊️ Reason: {reason}",
                        timestamp=datetime.utcnow(),
                        color=Color.from_rgb(27, 152, 250),
                    ).set_footer(text="Border hopping hispanic")
                    await member.move_to(channel=None)

                    channel = self.bot.get_channel(logs)

                    if logs is not None: 
                        await channel.send(
                            embed=embed2.set_thumbnail(url=interaction.user.avatar.url))
                        
                else:
                    await interaction.followup.send(
                    f"{interaction.user.mention}, {member.mention} is already Blacklisted.",
                    ephemeral=True)

        else:
            await interaction.followup.send(
                f"{interaction.user.mention}, {member.mention} is staff!",
                ephemeral=True)

    @blacklist.error
    async def on_blacklist_error(
        self, interaction: discord.Interaction, error: AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.followup.send(content=str(error), ephemeral=True)
            

    @app_commands.command(
        name="unblacklist", description="Unblacklists the passed user."
    )
    @app_commands.default_permissions(mute_members=True)
    @app_commands.describe(member='The member to unblacklist.', private='If the unblacklist message should be private.')
    async def unblacklist(self, interaction: discord.Interaction, member: discord.User, private:bool=False):
        print("[Unblacklist] has just been executed")

        await interaction.response.defer(ephemeral=private,thinking=True)
        db = await aiosqlite.connect("config.db")

     
        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )
        cur = await db.execute(
            f"""SELECT * FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        row = await cur.fetchone()
        if row is None:
            await interaction.followup.send(f'{interaction.user.mention}, to setup the blacklist command, run /setupblacklist')
            return

        res = await cur.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0]
        
        cur = await db.execute(f"""SELECT banned_role_id FROM blacklist WHERE guild_id = ?""", (interaction.guild.id, ))
        roleid = await cur.fetchone()
        if roleid is None:
            await interaction.followup.send(f'{interaction.user.mention}, to setup the blacklist command, run /setupblacklist')
            return
        role = discord.utils.get(interaction.guild.roles, id=roleid[0])
        if role in member.roles:
            await member.remove_roles(role)
            
            await interaction.followup.send(embed=discord.Embed(
                title='**Unblacklist**',
                description=f"> Unblacklisted: {member.mention}",color=Color.green()),
            )

            embed = discord.Embed(
                title="! **• UNBLACKLIST •** !",
                description=f"- 🧍 Issuer: {interaction.user.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`",
                timestamp=datetime.utcnow(),
                color=Color.from_rgb(27, 152, 250),
            )

            embed.set_footer(text="Border hopping hispanic")
            channel = self.bot.get_channel(logs)

            embed2 = discord.Embed(
                title="**Unblacklisted**",
                timestamp=datetime.utcnow(),
                description=f'**You were unblacklisted on "{interaction.guild.name}"**\n> Responsible: {interaction.user}\n ',
                color=Color.green()
            )

            embed2.set_footer(text="Border hopping hispanic")

            await member.send(
                embed=embed2,
            )
            if logs is not None:
                await channel.send(
                    embed=embed.set_thumbnail(url=interaction.user.avatar.url)
                )

        else:
            await interaction.followup.send(
                f"{interaction.user.mention}, {member} Is not Blacklisted.",
                ephemeral=True,
            )

    @unblacklist.error
    async def on_unblacklist_error(
        self, interaction: discord.Interaction, error: AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(content=str(error), ephemeral=True)

####################################################################################################################################
#################################################################################################################################### BLACKLIST END, MANAGENICK START
####################################################################################################################################

    @app_commands.command(name="managenick", description="Changes the passed user's nickname.")
    @app_commands.default_permissions(manage_nicknames=True)
    async def managenick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        nickname: str = None,
    ):
        print("[Managenick] has just been executed!")
        await interaction.response.defer(ephemeral=True, thinking=True)

        db = await aiosqlite.connect("config.db")


        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )
        cur = await db.execute(
            f"""SELECT * FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        row = await cur.fetchone()
        if row is None:
            await interaction.followup.send(f'{interaction.user.mention}, To setup {self.bot.user}\'s commands properly, run /logs to set a commands log channel')
            return

        res = await cur.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0] 

        await member.edit(nick=nickname)
        await interaction.followup.send(embed=discord.Embed(
            title='**Changed nick**',
            description=f'> Member: {member}\n> New nickname: "{nickname}"',color=Color.green()),
            ephemeral=True
        )

        chan = self.bot.get_channel(logs)

        embed = discord.Embed(
            title="! MANAGENICK !",
            description=f"- Issuer: {interaction.user.mention}\n- User: {member.mention}\n- Username: {member}\n- User Id: `{member.id}`\n- New nickname: {nickname}",
            color=Color.from_rgb(27, 152, 250),
        )

        await chan.send(embed=embed.set_thumbnail(url=interaction.user.avatar.url))

    @managenick.error
    async def on_managenick_error(self, interaction: discord.Interaction, error):
        await interaction.followup.send(content=str(error), ephemeral=True)

####################################################################################################################################
#################################################################################################################################### MANAGENICK END, MANAGEROLE START
####################################################################################################################################

    @app_commands.command(
        name="addrole", description="Gives the passed user the passed role"
    )
    @app_commands.describe(member='The member to give roles to.', role='The role to give to the member.', private='If the addrole message should be private.')
    @app_commands.default_permissions(manage_roles=True)
    async def addrole(
        self, interaction: discord.Interaction, member: discord.User, role: discord.Role, private:bool=False
    ) -> None:
        print("[Addrole] has just been executed")
        guild = interaction.guild

        await interaction.response.defer(ephemeral=private, thinking=True)

        db = await aiosqlite.connect("config.db")

        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )
        cur = await db.execute(
            f"""SELECT * FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        row = await cur.fetchone()
        if row is None:
            await cur.execute(
                """INSERT INTO logs VALUES(?,?,?,?)""",
                (interaction.guild.name, interaction.guild.id, None),
            )
            await db.commit()

        res = await cur.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0]

        role1 = interaction.guild.get_role(role.id)
        
        if role1 not in member.roles:
            await member.add_roles(role1)
            await interaction.followup.send(embed=discord.Embed(title='**Added role**',description= f"> Member: {member.mention}\n> Added role: <@&{role.id}>", color=Color.green()),ephemeral=private)
            

            embed2 = discord.Embed(
                title="! **• ADDROLE •** !",
                description=f"- 🧍 Issuer: {interaction.user.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n- 🔸 Role mention: <@&{role.id}>\n- 🔸 Role: {role}",
                timestamp=datetime.utcnow(),
                color=Color.from_rgb(27, 152, 250),
            )

            embed2.set_footer(text="Border hopping hispanic")

            channel = self.bot.get_channel(logs)

            if logs is not None:
                await channel.send(
                    embed=embed2.set_thumbnail(url=interaction.user.avatar.url)
                )
        else:
            await interaction.followup.send(embed=discord.Embed(title='**Add role**',description=f"> Error: {member.mention} already has <@&{role.id}>.",color=Color.red()),ephemeral=True)

    @app_commands.command(
        name="removerole", description="Removes the passed role from the passed user."
    )
    @app_commands.default_permissions(manage_roles=True)
    @app_commands.describe(member='The member to remove roles from.', role='The role to remove from the member.', private='If the removerole message should be private.')
    async def removerole(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        role: discord.Role,
        private:bool=False,
    ) -> None:
        print("[Removerole] has just been executed")
        await interaction.response.defer(ephemeral=private,thinking=True)
        guild = interaction.guild

        db = await aiosqlite.connect("config.db")

        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )
        cur = await db.execute(
            f"""SELECT * FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        row = await cur.fetchone()
        if row is None:
            await cur.execute(
                """INSERT INTO logs VALUES(?,?,?,?)""",
                (interaction.guild.name, interaction.guild.id, None),
            )
            await db.commit()

        res = await cur.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0]
        
        role1 = interaction.guild.get_role(role.id)
        if role1 in member.roles:
            await member.remove_roles(role1)
            await interaction.followup.send(embed=discord.Embed(
                title='**Removed role**',
                description=f"> Member: {member.mention}\n> Role removed: <@&{role.id}>",color=Color.red()),
            )

            embed2 = discord.Embed(
                title="! **• REMOVEROLE •** !",
                description=f"- 🧍 Issuer: {interaction.user.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n 🔸 Role mention: <@&{role.id}>\n- 🔸 Role: {role}",
                timestamp=datetime.utcnow(),
                color=Color.from_rgb(27, 152, 250),
            )

            embed2.set_footer(text="Border hopping hispanic")

            channel = self.bot.get_channel(logs)

            if logs is not None:
                await channel.send(
                    embed=embed2.set_thumbnail(url=interaction.user.avatar.url)
                )
        else:
            await interaction.followup.send(embed=discord.Embed(title='**Remove role**',description=f"> Error: {member.mention} does not have <@&{role.id}>.",color=Color.red()),ephemeral=True)

####################################################################################################################################
#################################################################################################################################### KYS END, PING START
####################################################################################################################################

async def setup(bot):
    await bot.add_cog(Moderation(bot))
