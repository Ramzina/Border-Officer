import discord
from discord.ext import commands
import aiosqlite
from datetime import timedelta
from discord import Color
import random
from discord import app_commands
from datetime import datetime
from discord.ext.commands import CommandNotFound, CommandOnCooldown, MissingPermissions, MissingRequiredArgument, has_permissions

from discord.app_commands import AppCommandError

chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
seperator = '-'

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.hybrid_command(name='roleall', description='Adds role to all users in guild.')
    @commands.has_permissions(administrator=True)
    async def roleall(self, ctx, role:discord.Role):
        await ctx.defer()

        msg = await ctx.send(embed=discord.Embed(description=f'Applying role, {role.mention} to {ctx.guild.member_count} users...', color=Color.yellow()))

        num = 0

        for member in ctx.guild.members:
            try:
                await member.add_roles(role)
                num += 1
            except:
                pass
        await msg.edit(embed=discord.Embed(description=f'Applied {role.mention} to {num} users successfully.', color=Color.green()))

    @commands.command(name='blacklistguild', description='Bot leaves the guild and blacklists it.')
    @commands.is_owner()
    async def guildblacklist(self, ctx, guild_id:int):
        db = await aiosqlite.connect("config.db")
        await db.execute("CREATE TABLE IF NOT EXISTS guildblacklist(guild_name TEXT, guild_id INTEGER)")
        msg = await ctx.send(embed=discord.Embed(description=f'<:yellowdot:1148198566448337018> Blacklisting guild: {guild_id}', color=Color.yellow()))
        for server in self.bot.guilds:
            if server.id == guild_id:
                try:
                    await server.system_channel.send(embed=discord.Embed(description=f'This guild has been blacklisted from using {self.bot.user}',color=Color.red()).set_image(url='https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.kym-cdn.com%2Fphotos%2Fimages%2Fnewsfeed%2F002%2F213%2F963%2F293.jpg&f=1&nofb=1&ipt=f823b62ebc7bd23f50b1d063696aa85d006f4e2d712cf7b62ad76c4507bdf968&ipo=images'))
                except:
                    pass
                await db.execute("INSERT INTO guildblacklist(guild_name, guild_id) VALUES(?,?)", (server.name,guild_id,))
                await db.commit()
                await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Blacklisted guild: {guild_id}, {server.name}', color=Color.green()))
                await server.leave()
                await db.close()
    @commands.command(name='unblacklistguild', description='Bot leaves the guild and blacklists it.')
    @commands.is_owner()
    async def unguildblacklist(self, ctx, guild_id:int):
        db = await aiosqlite.connect("config.db")
        await db.execute("CREATE TABLE IF NOT EXISTS guildblacklist(guild_name TEXT, guild_id INTEGER)")
        msg = await ctx.send(embed=discord.Embed(description=f'<:yellowdot:1148198566448337018> Blacklisting guild: {guild_id}', color=Color.yellow()))
        cur = await db.execute("SELECT guild_id FROM guildblacklist")
        res = await cur.fetchall()
        print(res)
        if not res:
            await msg.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> No guilds blacklisted.', color=Color.red()))
            return
        for id in res:
            if id[0] == guild_id:
                await db.execute("DELETE FROM guildblacklist WHERE guild_id = ?", (guild_id, ))
                await db.commit()
                await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Unblacklisted guild: {guild_id}', color=Color.green()))
                await db.close()
                return

        await msg.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Guild not blacklisted.', color=Color.red()))




####################################################################################################################################
#################################################################################################################################### BAN START
####################################################################################################################################




    @commands.hybrid_command(
        name="ban",
        description="Bans the user passed.",
    )
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, * ,reason: str = None):

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

            embed = discord.Embed(
                    title="**Banned**",
                    description=f'**You were banned from "{ctx.guild.name}"**\n> Reason: "{reason}"\n> Responsible: {ctx.author.mention}',
                    color=Color.red(),
                )
            
            try:
                await member.send(embed=embed)
            except:
                pass
            await member.ban(reason=reason)
            try:
                await ctx.send(embed=discord.Embed(
                title=f'**Ban**',
                description=f'> Banned: {member.mention}\n> Reason: "{reason}"',color=Color.red()),
                )
            except:
                pass

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
            await ctx.send(embed=discord.Embed(title='**Mute error**', description=f'> Error, logs are not setup. Use /logs', color=Color.red()))
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
    async def clear(
        self, ctx, member: discord.Member, amount: int
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
    async def purge(self, ctx, amount: int = 5):
        print("[Purge] has just been executed!")
        await ctx.defer()
        await ctx.message.delete()

        await ctx.channel.purge(limit=amount+1)
        await ctx.send(embed=discord.Embed(
                title='**Purge**',
                description=f"> Deleted: {amount} messages", color=Color.green()), delete_after=5.0)


    @purge.error
    async def on_purge_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Purge error**', description=f'> Error: {str(error)}', color=Color.red()))

####################################################################################################################################
#################################################################################################################################### PURGE END, BLACKLIST START
####################################################################################################################################
    @commands.hybrid_command(name='warn', description='Warns a user.')
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member:discord.Member, *,reason:str):
        print('[Warn] has just been executed.')
        await ctx.defer()
        warndb = await aiosqlite.connect("warns.db")
        await warndb.execute("""CREATE TABLE IF NOT EXISTS warns(guild_name TEXT, guild_id INTEGER, user_id INTEGER,warn_id TEXT, reason TEXT)""")

        configdb = await aiosqlite.connect("config.db")

        loggerton = await configdb.execute("SELECT channel_id FROM logs WHERE guild_id = ?", (ctx.guild.id, ))
        logs = await loggerton.fetchone()
        if not logs:
            await ctx.send(embed=discord.Embed(title='**Warn error**', description=f'> Error: Logs are not setup. Use /logs', color=Color.red()))
            return
        channel = logs[0]
        if ctx.author.top_role > member.top_role or member.top_role.permissions.administrator == False:
            chan = await ctx.guild.fetch_channel(channel)

            sec1 = random.choice(chars) + random.choice(chars) + random.choice(chars) + random.choice(chars)
            sec2 = random.choice(chars) + random.choice(chars) + random.choice(chars) + random.choice(chars)
            sec3 = random.choice(chars) + random.choice(chars) + random.choice(chars) + random.choice(chars)
            warnid = f'{sec1}{seperator}{sec2}{seperator}{sec3}'

            await ctx.send(embed=discord.Embed(title='**Warned**', description=f'> Warned {member.mention}\n> Reason: `{reason}`\n> Warn Id: `{warnid}`', color=Color.red()))

            try:
                await member.send(embed=discord.Embed(title='**Warned**', description=f'**You have been warned on "{ctx.guild.name}"**\n> Reason: `{reason}`\n> Warn Id: `{warnid}`\n> Responsible: {ctx.author}', color=Color.red()))
            except:
                pass
            await warndb.execute("""INSERT INTO warns(guild_name, guild_id, user_id,warn_id, reason) VALUES(?,?,?,?,?)""", (ctx.guild.name, ctx.guild.id, member.id,warnid, reason, ))
            await warndb.commit()
            embed2 = discord.Embed(
                title="**! • WARN • !**",
                description=f"- 🧍 Issuer: {ctx.author.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n- 🖊️ Warn Context: {reason}\n- Warn Id: `{warnid}`",
                color=Color.blurple(),
                    )
            await chan.send(embed=embed2.set_thumbnail(url=ctx.author.avatar.url))
            await configdb.close()
            await warndb.close()
        else:
            await ctx.send(embed=discord.Embed(title='**Warn Error**', description='> Error: You cannot warn this user.', color=Color.red()))
            return
    @warn.error
    async def on_warn_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Warn error**', description=f'> Error: {str(error)}', color=Color.red()))
    @commands.hybrid_command(name='removewarn', description='Deletes a users warn.')
    @commands.has_permissions(moderate_members=True)
    async def removewarn(self, ctx, member:discord.Member,warn_id:str):
        print('[Removewarn] has just been executed.')
        await ctx.defer()
        warndb = await aiosqlite.connect("warns.db")
        await warndb.execute("""CREATE TABLE IF NOT EXISTS warns(guild_name TEXT, guild_id INTEGER, user_id INTEGER,warn_id TEXT, reason TEXT)""")

        configdb = await aiosqlite.connect("config.db")

        loggerton = await configdb.execute("SELECT channel_id FROM logs WHERE guild_id = ?", (ctx.guild.id, ))
        logs = await loggerton.fetchone()
        if not logs:
            await ctx.send(embed=discord.Embed(title='**Warn error**', description=f'> Error: Logs are not setup. Use /logs', color=Color.red()))
            return
        channel = logs[0]
        if ctx.author.top_role > member.top_role or member.top_role.permissions.administrator == False:
            chan = await ctx.guild.fetch_channel(channel)

            cur = await warndb.execute("SELECT warn_id, reason FROM warns WHERE guild_id = ? AND user_id = ? AND warn_id = ?", (ctx.guild.id, member.id, warn_id, ))
            res = await cur.fetchall()
            if not res:
                await ctx.send(embed=discord.Embed(title='Removewarn Error', description=f'> Error: `{warn_id}` is an invalid warn id.', color=Color.red()))
                return

            cur = res[0]

            await ctx.send(embed=discord.Embed(title='**Warn Removed**', description=f'> Warn removed from {member.mention}\n> Warn Id: `{cur[0]}`\n> Warn Context: {cur[1]}', color=Color.green()))

            try:
                await member.send(embed=discord.Embed(title='**Warn Removed**', description=f'**A warn was removed on "{ctx.guild.name}"**\n> Reason: `{cur[1]}`\n> Warn Id: `{cur[0]}`\n> Responsible: {ctx.author}', color=Color.green()))
            except:
                pass
            await warndb.execute("""DELETE FROM warns WHERE guild_id = ? AND warn_id = ? AND user_id = ? """, (ctx.guild.id, cur[0], member.id, ))
            await warndb.commit()
            embed2 = discord.Embed(
                title="**! • WARN REMOVED • !**",
                description=f"- 🧍 Issuer: {ctx.author.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n- 🖊️ Warn Context: {cur[1]}\n- Warn Id: `{cur[0]}`",
                color=Color.blurple(),
                    )
            await chan.send(embed=embed2.set_thumbnail(url=ctx.author.avatar.url))
            await configdb.close()
            await warndb.close()
        else:
            await ctx.send(embed=discord.Embed(title='**Warn Error**', description='> Error: You cannot warn this user.', color=Color.red()))
            return
    @removewarn.error
    async def on_removewarn_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Removewarn error**', description=f'> Error: {str(error)}', color=Color.red()))
    @commands.hybrid_command(name='warns', description='Shows the warns of a user.')
    async def warns(self, ctx, member:discord.Member=None):
        await ctx.defer()

        warndb = await aiosqlite.connect("warns.db")
        await warndb.execute("CREATE TABLE IF NOT EXISTS warns(guild_name TEXT, guild_id INTEGER, user_id INTEGER,warn_id TEXT, reason TEXT)")

        if member is None:
            member = ctx.author

        res = await warndb.execute("SELECT reason, warn_id FROM warns WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, member.id, ))
        warntuple = await res.fetchall()
        if not warntuple:
            await ctx.send(embed=discord.Embed(title="**Warns Error**", description=f'> Error: {member} has no warns.', color=Color.red()))
            return
        warnthing = warntuple[0]
        warnsids = warnthing[1]

        warns = [f"\n> **{warn[0]}** | `{warn[1]}`" for warn in warntuple]

        embed = discord.Embed(title=f'{member}\'s Warns', description=''.join(warns), color=Color.blurple()).set_footer(text='WARN REASON, WARN ID')
        await ctx.send(embed=embed)
    @warns.error
    async def on_warns_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Warns error**', description=f'> Error: {str(error)}', color=Color.red()))

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
            await ctx.send(embed=discord.Embed(title='**Blacklist error**', description=f'> Error: Blacklist is not setup. Use /logs', color=Color.red()))
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
    async def on_managenick_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Managenick error**', description=f'> Error: {str(error)}', color=Color.red()))

####################################################################################################################################
#################################################################################################################################### MANAGENICK END, MANAGEROLE START
####################################################################################################################################

    @commands.hybrid_command(
        name="addrole", description="Gives the passed user the passed role"
    )
    @commands.has_permissions(manage_roles=True)
    async def addrole(
        self, ctx, member: discord.Member, role: discord.Role
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

        if channel is None:
            await ctx.send(f'To setup {self.bot.user}\'s commands properly, run /help and choose the setup section')
            return
        
        if role not in member.roles:
            await member.add_roles(role)
            await ctx.send(embed=discord.Embed(title='**Added role**',description= f"> Member: {member.mention}\n> Added role: <@&{role.id}>", color=Color.green()))
            

            embed2 = discord.Embed(
                title="! **• ADDROLE •** !",
                description=f"- 🧍 Issuer: {ctx.author.mention}\n- 🧍 User: {member.mention}\n- 🪪 User name: {member}\n- 🪪 User Id: `{member.id}`\n- 🔸 Role mention: <@&{role.id}>\n- 🔸 Role: {role}",
                timestamp=datetime.utcnow(),
                color=Color.blurple(),
            )

            channel = self.bot.get_channel(logs)

            if not logs:
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
        cur = await db.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {ctx.guild.id}"""
        )
        res = await cur.fetchone()
        logs = res[0]
        await cur.close()
        if not res:
            await ctx.send(f'Run /logs to setup the logs channel.')
            return

        if role in member.roles:
            await member.remove_roles(role)
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

            if not logs:
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
    @commands.has_permissions(manage_messages=True)
    async def lockdown(self, ctx, channel:discord.TextChannel=None):
        await ctx.defer()

        if not channel:
            channel = ctx.channel

        db = await aiosqlite.connect("config.db")

        await db.execute("""CREATE TABLE IF NOT EXISTS lockdown(guild_name STRING, guild_id INTEGER, locked_role INTEGER)""")


        cur = await db.execute("""SELECT locked_role FROM lockdown WHERE guild_id = ?""", (ctx.guild.id, ))
        role_id = await cur.fetchone()

        if not role_id:
            role_id = None
            role = ctx.guild.default_role
        else:
            role = ctx.guild.get_role(role_id[0])
        x = channel.permissions_for(role)
        if x.send_messages:
            await channel.set_permissions(role, send_messages = False, create_public_threads=False, create_private_threads=False)
            await ctx.send(embed=discord.Embed(title='**Locked**', description=f'> Locked channel: <#{channel.id}>\n> Locked by: {ctx.author.mention}', color=Color.green()))
        else:
            await ctx.send(embed=discord.Embed(title='**Lock error**', description=f'> Error: <#{channel.id}> `is not locked.`', color=Color.red()))
    @lockdown.error
    async def on_lockdown_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Lock error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='unlock', description='Locks the selected channel.')
    @commands.has_permissions(manage_messages=True)
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
