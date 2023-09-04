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

    @commands.hybrid_command(
        name="ban",
        description="Bans the passed user.",
    )
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.User, * ,reason: str = None):

        print("[Ban] has just been executed")
        await ctx.defer()

        db = await aiosqlite.connect("config.db")

        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )


        res = await db.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {ctx.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0]


        if channel is None:
            await ctx.send(embed=discord.Embed(title='**Blacklist error**', description=f'> Error: Logs are not setup. Use /logs', color=Color.red()))
            return
        if member not in ctx.guild.members:
            await ctx.send(embed=discord.Embed(title='**Blacklist error**', description=f'> Error: {member.mention} is not in the guild. Use /hackban', color=Color.red()))
            return
        if ctx.author.top_role > member.top_role or member.top_role.permissions.administrator == False:

            try:
                embed = discord.Embed(
                    title="**Banned**",
                    description=f'**You were banned from "{ctx.guild.name}"**\n> Reason: "{reason}"\n> Responsible: {ctx.author.mention}',
                    color=Color.red(),
                )
            except:
                pass
            
            if member in ctx.guild.members:
                await member.send(embed=embed)
                
            await ctx.guild.ban(member=member, reason=reason)
            await ctx.send(embed=discord.Embed(
                title=f'**Ban**',
                description=f'> Banned: {member.mention}\n> Reason: "{reason}"',color=Color.red()),
            )

            embed2 = discord.Embed(
                title="! **• BAN •** !",
                description=f"- 🧍 Issuer: {ctx.author.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n- 🖊️ Reason: {reason}",
                timestamp=datetime.utcnow(),
                color=Color.blurple(),
            )


            channel = self.bot.get_channel(logs)


            await channel.send(
                embed=embed2.set_thumbnail(url=ctx.author.avatar.url)
                )
        else:
            await ctx.send(embed=discord.Embed(title='**Blacklist error**', description=f'> Error: You cannot ban {member.mention}.', color=Color.red()))
    @ban.error
    async def on_ban_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Ban error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(
        name="hackban",
        description="Bans the passed user.",
    )
    @commands.has_permissions(ban_members=True)
    async def hackban(
        self, ctx, member: discord.User, *,reason: str = None
   ):
        
        print("[Hackban] has just been executed")
        await ctx.defer()

        db = await aiosqlite.connect("config.db")

        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )


        res = await db.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {ctx.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0]


        if channel is None:
            await ctx.send(embed=discord.Embed(title='**Hackban error**', description=f'> Error: Logs are not setup. Use /logs', color=Color.red()))
            return
        
        if member not in ctx.guild.members:
                
            await ctx.guild.ban(user=member, reason=reason)
            await ctx.send(embed=discord.Embed(
                title=f'**Ban**',
                description=f'> Banned: {member.mention}\n> Reason: "{reason}"',color=Color.red()),
            )

            embed2 = discord.Embed(
                title="! **• BAN •** !",
                description=f"- 🧍 Issuer: {ctx.author.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n- 🖊️ Reason: {reason}",
                timestamp=datetime.utcnow(),
                color=Color.blurple(),
            )


            channel = self.bot.get_channel(logs)


            await channel.send(
                embed=embed2.set_thumbnail(url=ctx.author.avatar.url)
                )
        else:
            await ctx.send(embed=discord.Embed(title='**Hackban error**', description=f'> Error: {member.mention} is in the guild.', color=Color.red()))
         

    @hackban.error
    async def on_hackban_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Hackban error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='unban', description="Unbans the passed user.")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: discord.User):
            print("[Unban] has just been executed")
            await ctx.defer()

            db = await aiosqlite.connect("config.db")

            await db.execute(
                """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
            )

            res = await db.execute(
                f"""SELECT channel_id FROM logs WHERE guild_id = {ctx.guild.id}"""
            )
            channel = await res.fetchone()
            logs = channel[0]          

            if channel is None:
                await ctx.send(embed=discord.Embed(title='**Unban error**', description=f'> Error: Logs are not setup. Use /logs', color=Color.red()))
                return

            await ctx.guild.unban(member)
            await ctx.send(embed=discord.Embed(
                title='**Unban**',
                description=f"> Unbanned: {member.mention}",color=Color.green()),
            )

            embed2 = discord.Embed(
                title="! **• UNBAN •** !",
                description=f"- 🧍 Issuer: {ctx.author.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`",
                timestamp=datetime.utcnow(),
                color=Color.blurple(),
            )

            channel = self.bot.get_channel(logs)

            if logs is not None:
                await channel.send(
                    embed=embed2.set_thumbnail(url=ctx.author.avatar.url)
                )

    @unban.error
    async def on_unban_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Unban error**', description=f'> Error: {str(error)}', color=Color.red()))

####################################################################################################################################
#################################################################################################################################### BAN END, MUTE START
####################################################################################################################################


    @commands.hybrid_command(name="mute", description="Tempmutes the passed user.")
    @commands.has_permissions(moderate_members=True)
    async def mute(
        self,
        ctx,
        member: discord.Member,
        minutes: int = 10,
        hours: int = 0,
        days: int = 0,
        *,
        reason: str = None,
    ):
        print("[Mute] has just been executed")
        await ctx.defer()

        db = await aiosqlite.connect("config.db")

        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )

        res = await db.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {ctx.guild.id}"""
        )
        channel = await res.fetchone()

        logs = channel[0]

        if channel is None:
            await ctx.send(embed=discord.Embed(title='**Blacklist error**', description=f'> Error, logs are not setup. Use /logs', color=Color.red()))
            return

        if ctx.author.top_role > member.top_role or member.top_role.permissions.administrator == False:

            if member.is_timed_out() == False:
                delta = timedelta(minutes=minutes, hours=hours, days=days)

                await member.timeout(delta, reason=reason)
                await ctx.send(embed=discord.Embed(
                    title='**Mute**',
                    description=f'> Muted: {member.mention}\n> Reason: "{reason}"',color=Color.red()),
                )
                
                embed = discord.Embed(
                    title="**Muted**",
                    description=f'**You were muted in "{ctx.guild.name}"**\n> Reason: `{reason}`\n> Responsible: {ctx.author}\n> Duration: {minutes}m, {hours}h, {days}d',
                    color=Color.red(),
                )
                try:
                    await member.send(
                    embed=embed,
                    )
                except:
                    pass

                embed2 = discord.Embed(
                    title="! **• MUTE •** !",
                    description=f"- 🧍 Issuer: {ctx.author.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n- 🖊️ Reason: {reason}",
                    timestamp=datetime.utcnow(),
                    color=Color.blurple(),
                )

                await member.move_to(None)

                if logs is not None:
                    channel = self.bot.get_channel(logs)

                    await channel.send(
                        embed=embed2.set_thumbnail(url=ctx.author.avatar.url)
                    )

            else:
                await ctx.send(embed=discord.Embed(title='**Mute error**', description=f'> Error: {member.mention} is already muted.', color=Color.red()))

        else:
            await ctx.send(embed=discord.Embed(title='**Mute error**', description=f'> Error: You cannot mute {member.mention}.', color=Color.red()))
    @mute.error
    async def on_mute_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Mute error**', description=f'> Error: {str(error)}', color=Color.red()))


    @commands.hybrid_command(
        name="unmute", description="Unmutes the passed user."
    )
    @commands.has_permissions(moderate_members=True)
    async def unmute(self, ctx, member: discord.Member):
        print("[Unmute] has just been executed")
        await ctx.defer()

        db = await aiosqlite.connect("config.db")

        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )

        res = await db.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {ctx.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0]

        if channel is None:
            await ctx.send(embed=discord.Embed(title='**Unmute error**', description=f'> Error: Logs not setup. Run /logs', color=Color.red()))
            return

        if member.is_timed_out() == True:
            await member.timeout(None)

            
            await ctx.send(embed=discord.Embed(
                    title='**Unmute**',
                    description=f"> Unmuted: {member.mention}",color=Color.green()),
                )

            embed = discord.Embed(
                title="! **• UNMUTE •** !",
                description=f"- 🧍 Issuer: {ctx.author.mention}\n-🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`",
                color=Color.blurple(),
            )

            channel = self.bot.get_channel(logs)

            embed2 = discord.Embed(
                title="**Unmuted**",
                description=f'**You were unmuted in "{ctx.guild.name}"**\n> Responsible: {ctx.author}\n ',
                color=Color.green()
            )
            try:
                await member.send(
                embed=embed2,
                )
            except:
                pass


            await channel.send(
                embed=embed.set_thumbnail(url=(ctx.author.avatar.url))
            )
        else:
            await ctx.send(embed=discord.Embed(title='**Unmute error**', description=f'> Error: {member.mention} is not muted.', color=Color.red()))
    @unmute.error
    async def on_unmute_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Unmute error**', description=f'> Error: {str(error)}', color=Color.red()))

####################################################################################################################################
#################################################################################################################################### MUTE END, KICK START
####################################################################################################################################

    @commands.hybrid_command(
        name="kick", description="Kicks the passed user."
    )
    @commands.has_permissions(kick_members=True)
    async def kick(
        self, ctx, member: discord.Member,* ,reason: str=None,
    ):
        print("[Kick] has just been executed")
        await ctx.defer()

        db = await aiosqlite.connect("config.db")

        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )
        res = await db.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {ctx.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0]
        if channel is None:
            await ctx.send(embed=discord.Embed(title='**Kick error**', description=f'> Error: Blacklist is not setup. Use /setupblacklist', color=Color.red()))
            return



        if ctx.author.top_role > member.top_role or member.top_role.permissions.administrator == False:
            invite = await ctx.guild.text_channels[0].create_invite(max_age=0, max_uses=1, unique=True)

            embed = discord.Embed(title='**Kicked**',
                description=f'**You were kicked from "{ctx.guild.name}"**\n> Reason: `{reason}`\n> Responsible: {ctx.author}\n> \n> [Rejoin {ctx.guild.name}]({invite})',
                color=Color.red(),
            )
            try:
                await member.send(
                    embed=embed,
                )
            except:
                pass
            await ctx.send(embed=discord.Embed(
                title='**Kick**',
                description=f'> Kicked: {member.mention}\n> Reason: "{reason}"',color=Color.red()),
            )
            await member.kick(reason=reason)

            embed2 = discord.Embed(
                title="! **• KICK •** !",
                description=f"- 🧍 Issuer: {ctx.author.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n- 🖊️ Reason: {reason}",
                color=Color.blurple(),
            )

            channel = self.bot.get_channel(logs)

            if logs is not None:
                await channel.send(
                    embed=embed2.set_thumbnail(url=ctx.author.avatar.url)
                )
        else:
            await ctx.send(embed=discord.Embed(title='**Kick error**', description=f'> Error: You cannot kick {member.mention}.', color=Color.red()))

    @kick.error
    async def on_kick_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Kick error**', description=f'> Error: {str(error)}', color=Color.red()))

####################################################################################################################################
#################################################################################################################################### KICK END, CLEAR START
####################################################################################################################################

    @commands.hybrid_command(name="clear", description="Clears messages from the passed user")
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def clear(
        self, ctx, member: discord.User, amount: int
    ):
        print("[Clear] has just been executed")
        await ctx.defer()


        def check_author(m):
            return m.author.id == member.id
        

        await ctx.channel.purge(limit=amount, check=check_author)
        await ctx.send(embed=discord.Embed(title='**Clear**', description=f'> Messages cleared: `{amount}`',color=Color.green()),delete_after=5.0)

    @clear.error
    async def on_clear_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Clear error**', description=f'> Error: {str(error)}', color=Color.red()))

####################################################################################################################################
#################################################################################################################################### CLEAR END, PURGE START
####################################################################################################################################

    @commands.hybrid_command(
        name="purge", description="Deletes the passed amount of messages."
    )
    @commands.has_permissions(manage_messages=True)
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def purge(self, ctx, amount: int = 5):
        print("[Purge] has just been executed!")
        await ctx.defer()

        floor = 2
        ceiling = 50
    
       
        if amount >= floor and amount <= ceiling:
            await ctx.channel.purge(limit=amount+1)
            await ctx.send(embed=discord.Embed(
                title='**Purge**',
                description=f"> Deleted: {amount} messages", color=Color.green()),delete_after=5.0)
           

        elif amount < floor:
            await ctx.send(embed=discord.Embed(
                title='**Purge**',
                description=f"> Error: Amount is less than `{floor}`\n> Usage example: `/purge 5`",color=Color.red()),delte_after=5.0)
            

        elif amount > ceiling:
            await ctx.send(embed=discord.Embed(
                title='**Purge**',
                description=f"> Error: Amount must be less than `{ceiling}`\n> Usage example: `/purge 5`",color=Color.red()),delete_after=5.0)

    @purge.error
    async def on_purge_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Purge error**', description=f'> Error: {str(error)}', color=Color.red()))

####################################################################################################################################
#################################################################################################################################### PURGE END, BLACKLIST START
####################################################################################################################################
            
    @commands.hybrid_command(
        name="blacklist", description="Blacklists the passed user."
    )
    @commands.has_permissions(moderate_members=True)
    async def blacklist(self, ctx, member: discord.Member, *,reason: str):
        
        print("[Blacklist] has just been executed")
        await ctx.defer()


        db = await aiosqlite.connect("config.db")


        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )

        res = await db.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = ?""", (ctx.guild.id, )
        )
        channel = await res.fetchone()

        if channel is None:
            await ctx.send(embed=discord.Embed(title='**Blacklist error**', description=f'> Error: Blacklist is not setup. Use /setupblacklist', color=Color.red()))
            return

        logs = channel[0] 


        if ctx.author.top_role > member.top_role or member.top_role.permissions.administrator == False:

                cur = await db.execute(f"""SELECT banned_role_id FROM blacklist WHERE guild_id = ?""", (ctx.guild.id, ))
                roleid = await cur.fetchone()
                if roleid is None:
                    await ctx.send(embed=discord.Embed(title='**Blacklist error**', description=f'> Error: Blacklist is not setup. Use /setupblacklist', color=Color.red()))
                    return

                role = ctx.guild.get_role(roleid[0])
                if role not in member.roles:

                    await member.add_roles(role)

                    
                    await ctx.send(embed=discord.Embed(
                        title='**Blacklist**',
                        description=f'> Blacklisted: {member.mention}\n> Reason: "{reason}"',color=Color.red()))

                    embed = discord.Embed(
                        title="**Blacklisted**",
                        description=f'**You have been blacklisted on "{ctx.guild.name}"**\n> Reason: `{reason}`\n> Responsible: {ctx.author}\n ',
                        color=Color.red(),
                    )
                    try:
                        await member.send(
                            embed=embed)
                    except:
                        pass
                    
                    embed2 = discord.Embed(
                        title="**! • BLACKLIST • !**",
                        description=f"- 🧍 Issuer: {ctx.author.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n- 🖊️ Reason: {reason}",
                        color=Color.blurple(),
                    )
                    await member.move_to(channel=None)

                    channel = self.bot.get_channel(logs)

                    await channel.send(embed=embed2.set_thumbnail(url=ctx.author.avatar.url))
                        
                else:
                    await ctx.send(embed=discord.Embed(title='**Blacklist error**', description=f'> Error: {member.mention} is already blacklisted.', color=Color.red()))

        else:
            await ctx.send(embed=discord.Embed(title='**Blacklist error**', description=f'> Error: You cannot blacklist {member.mention}.', color=Color.red()))

    @blacklist.error
    async def on_blacklist_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Blacklist error**', description=f'> Error: {str(error)}', color=Color.red()))
            

    @commands.hybrid_command(
        name="unblacklist", description="Unblacklists the passed user."
    )
    @commands.has_permissions(moderate_members=True)
    async def unblacklist(self, ctx, member: discord.Member):
        print("[Unblacklist] has just been executed")

        await ctx.defer()
        db = await aiosqlite.connect("config.db")

     
        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )

        res = await db.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {ctx.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0]

        if channel is None:
            await ctx.send(embed=discord.Embed(title='**Unblacklist error**', description=f'> Error: Blacklist command not setup. use /setupblacklist', color=Color.red()))
            return
        
        cur = await db.execute(f"""SELECT banned_role_id FROM blacklist WHERE guild_id = ?""", (ctx.guild.id, ))
        roleid = await cur.fetchone()
        if roleid is None:
            await ctx.send(embed=discord.Embed(title='**Unblacklist error**', description=f'> Error: Blacklist command not setup. use /setupblacklist', color=Color.red()))
            return
        
        role = discord.utils.get(ctx.guild.roles, id=roleid[0])
        if role in member.roles:
            await member.remove_roles(role)
            
            await ctx.send(embed=discord.Embed(
                title='**Unblacklist**',
                description=f"> Unblacklisted: {member.mention}",color=Color.green()),
            )

            embed = discord.Embed(
                title="! **• UNBLACKLIST •** !",
                description=f"- 🧍 Issuer: {ctx.author.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`",
                color=Color.blurple(),
            )


            channel = self.bot.get_channel(logs)

            embed2 = discord.Embed(
                title="**Unblacklisted**",
                description=f'**You were unblacklisted on "{ctx.guild.name}"**\n> Responsible: {ctx.author}\n ',
                color=Color.green()
            )
            try:
                await member.send(
                embed=embed2,
                )
            except:
                pass
            if logs is not None:
                await channel.send(
                    embed=embed.set_thumbnail(url=ctx.author.avatar.url)
                )

        else:
            await ctx.send(embed=discord.Embed(title='**Unblacklist error**', description=f'> Error: {member.mention} is not blacklisted.', color=Color.red()))

    @unblacklist.error
    async def on_unblacklist_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Unblacklist error**', description=f'> Error: {str(error)}', color=Color.red()))

####################################################################################################################################
#################################################################################################################################### BLACKLIST END, MANAGENICK START
####################################################################################################################################

    @commands.hybrid_command(name="managenick", description="Changes the passed user's nickname.")
    @commands.has_permissions(manage_nicknames=True) 
    async def managenick(
        self,
        ctx,
        member: discord.Member,
        *,
        nickname: str,
    ):
        print("[Managenick] has just been executed!")
        await ctx.defer()

        db = await aiosqlite.connect("config.db")


        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )

        res = await db.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {ctx.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0] 

        if channel is None:
            await ctx.send(f'{ctx.author.mention}, To setup {self.bot.user}\'s commands properly, run /logs to set a commands log channel')
            return
        if member.top_role < ctx.author.top_role and  member.top_role < self.bot.top_role:
            await member.edit(nick=nickname)
            await ctx.send(embed=discord.Embed(
            title='**Changed nick**',
            description=f'> Member: {member}\n> New nickname: "{nickname}"',color=Color.green()),
            ephemeral=True
            )
        

            chan = self.bot.get_channel(logs)

            embed = discord.Embed(
                title="! MANAGENICK !",
                description=f"- Issuer: {ctx.author.mention}\n- User: {member.mention}\n- Username: {member}\n- User Id: `{member.id}`\n- New nickname: {nickname}",
                color=Color.from_rgb(27, 152, 250),
            )

            await chan.send(embed=embed.set_thumbnail(url=ctx.author.avatar.url))
            return
        await ctx.send(embed=discord.Embed(title='**Managenick error**', description=f'> Error: You or the bot cannot edit this user.', color=Color.red()))


    @managenick.error
    async def on_addrole_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Managenick error**', description=f'> Error: {str(error)}', color=Color.red()))

####################################################################################################################################
#################################################################################################################################### MANAGENICK END, MANAGEROLE START
####################################################################################################################################

    @commands.hybrid_command(
        name="addrole", description="Gives the passed user the passed role"
    )
    @commands.has_permissions(manage_roles=True)
    async def addrole(
        self, ctx, member: discord.User, role: discord.Role
    ):
        print("[Addrole] has just been executed")
        await ctx.defer()

        db = await aiosqlite.connect("config.db")

        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )

        res = await db.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {ctx.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0]

        role1 = ctx.guild.get_role(role.id)

        if channel is None:
            await ctx.send(f'To setup {self.bot.user}\'s commands properly, run /help and choose the setup section')
            return

        
        if role1 not in member.roles:
            await member.add_roles(role1)
            await ctx.send(embed=discord.Embed(title='**Added role**',description= f"> Member: {member.mention}\n> Added role: <@&{role.id}>", color=Color.green()))
            

            embed2 = discord.Embed(
                title="! **• ADDROLE •** !",
                description=f"- 🧍 Issuer: {ctx.author.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n- 🔸 Role mention: <@&{role.id}>\n- 🔸 Role: {role}",
                timestamp=datetime.utcnow(),
                color=Color.blurple(),
            )

            channel = self.bot.get_channel(logs)

            if logs is not None:
                await channel.send(
                    embed=embed2.set_thumbnail(url=ctx.author.avatar.url)
                )
        else:
            await ctx.send(embed=discord.Embed(title='**Addrole**',description=f"> Error: {member.mention} already has <@&{role.id}>.",color=Color.red()),ephemeral=True)
    @addrole.error
    async def on_addrole_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Addrole error**', description=f'> Error: {str(error)}', color=Color.red()))
            
            
    @commands.hybrid_command(
        name="removerole", description="Removes the passed role from the passed user."
    )
    @commands.has_permissions(manage_roles=True)
    async def removerole(
        self,
        ctx,
        member: discord.Member,
        role: discord.Role,
        ):
        print("[Removerole] has just been executed")
        await ctx.defer()

        db = await aiosqlite.connect("config.db")

        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )
        res = await db.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {ctx.guild.id}"""
        )
        cur = await res.fetchone()
        logs = channel[0]
        
        role1 = ctx.guild.get_role(role.id)

        res = await cur.fetchone()
        if res is None:
            await ctx.send(f'To setup {self.bot.user}\'s commands properly, run /help and choose the setup section')
            return

        if role1 in member.roles:
            await member.remove_roles(role1)
            await ctx.send(embed=discord.Embed(
                title='**Removed role**',
                description=f"> Member: {member.mention}\n> Role removed: <@&{role.id}>",color=Color.red()),
            )

            embed2 = discord.Embed(
                title="! **• REMOVEROLE •** !",
                description=f"- 🧍 Issuer: {ctx.author.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n 🔸 Role mention: <@&{role.id}>\n- 🔸 Role: {role}",
                color=Color.blue(),
            )

            channel = self.bot.get_channel(logs)

            if logs is not None:
                await channel.send(
                    embed=embed2.set_thumbnail(url=ctx.author.avatar.url)
                )
        else:
            await ctx.send(embed=discord.Embed(title='**Removerole**',description=f"> Error: {member.mention} does not have <@&{role.id}>.",color=Color.red()))

    @removerole.error
    async def on_removerole_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Removerole error**', description=f'> Error: {str(error)}', color=Color.red()))
            
####################################################################################################################################
#################################################################################################################################### KYS END, PING START
####################################################################################################################################

    @commands.hybrid_command(name='lockdown', description='Locks the selected channel.')
    @commands.has_permissions(manage_channels=True)
    async def lockdown(self, ctx, channel:discord.TextChannel=None):
        await ctx.defer()

        if channel==None:
            channel = ctx.channel

        db = await aiosqlite.connect("config.db")

        await db.execute("""CREATE TABLE IF NOT EXISTS lockdown(guild_name STRING, guild_id INTEGER, locked_role INTEGER)""")


        cur = await db.execute("""SELECT locked_role FROM lockdown WHERE guild_id = ?""", (ctx.guild.id, ))
        role_id = await cur.fetchone()

        if role_id is None:

            x2 = channel.permissions_for(ctx.guild.default_role)

            if x2.send_messages:
                await channel.set_permissions(ctx.guild.default_role, send_messages = False, create_public_threads=False, create_private_threads=False)
                await ctx.send(embed=discord.Embed(title='**Locked**', description=f'> Locked channel: <#{channel.id}>\n> Locked by: {ctx.author.mention}', color=Color.green()))
                return
            else:
                await ctx.send(embed=discord.Embed(title='**Lock error**', description=f'> Error: <#{channel.id}> `is not locked.`', color=Color.red()))
                return

        if role_id is not None:

            role = ctx.guild.get_role(role_id[0])
            x = channel.permissions_for(role)

            if x.send_messages:
                await channel.set_permissions(role, send_messages = False, create_public_threads=False, create_private_threads=False)
                await ctx.send(embed=discord.Embed(title='**Locked**', description=f'> Locked channel: <#{channel.id}>\n> Locked by: {ctx.user.mention}', color=Color.green()))
            else:
                await ctx.followup.send(embed=discord.Embed(title='**Lock error**', description=f'> Error: <#{channel.id}> `is not locked.`', color=Color.red()))
    @lockdown.error
    async def on_lockdown_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Lock error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='unlock', description='Locks the selected channel.')
    @commands.has_permissions(manage_channels=True)
    async def unlock(self, ctx, channel:discord.TextChannel=None):
        await ctx.defer()

        if channel==None:
            channel = ctx.channel

        db = await aiosqlite.connect("config.db")

        await db.execute("""CREATE TABLE IF NOT EXISTS lockdown(guild_name STRING, guild_id INTEGER, locked_role INTEGER)""")

        cur = await db.execute("""SELECT locked_role FROM lockdown WHERE guild_id = ?""", (ctx.guild.id, ))
        role_id = await cur.fetchone()

        if role_id is None:

            x2 = channel.permissions_for(ctx.guild.default_role)

            if not x2.send_messages:
                await channel.set_permissions(ctx.guild.default_role, send_messages = True)
                await ctx.send(embed=discord.Embed(title='**Unlocked**', description=f'> Unlocked channel: <#{channel.id}>\n> Unlocked by: {ctx.author.mention}', color=Color.green()))
                return
            else:
                await ctx.send(embed=discord.Embed(title='**Unlock error**', description=f'> Error: <#{channel.id}> `is not locked for <&@{role_id}>`', color=Color.red()))

        else:

            role = ctx.guild.get_role(role_id[0])
            x = channel.permissions_for(role)

            if not x.send_messages:            
                await channel.set_permissions(role, send_messages = True)
                await ctx.send(embed=discord.Embed(title='**Unlocked**', description=f'> Unlocked channel: <#{channel.id}>\n> Unlocked by: {ctx.author.mention}', color=Color.green()))
                return            
            else:
                await ctx.send(embed=discord.Embed(title='**Unlock error**', description=f'> Error: <#{channel.id}> `is not locked for <&@{role_id}>`', color=Color.red()))

    @unlock.error
    async def on_unlock_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Unlock error**', description=f'> Error: {str(error)}', color=Color.red()))


async def setup(bot):
    await bot.add_cog(Moderation(bot))
