import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button,button, View
import random
from TOD.dare import dare
import asyncio
from TOD.truth import truth
from typing import Literal
from discord.app_commands import AppCommandError
from discord import Color
from datetime import datetime
import aiosqlite

chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
seperator = '-'

class Community(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

####################################################################################################################################
#################################################################################################################################### NICK START
####################################################################################################################################

    @commands.hybrid_command(name="nick", description="Changes your nickname.")
    @commands.has_permissions(change_nickname=True)
    async def nick(self, ctx, *,nickname: str = None):
        print("[Nick] has just been executed!")
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.defer()


        db = await aiosqlite.connect("config.db")


        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )
            
        res = await db.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {ctx.guild.id}"""
        )
        channel = await res.fetchone()

        if channel is None: await ctx.send(embed=discord.Embed(title='**Nick error**', description=f'> Error: Logs are not setup. Use /logs if you are staff', color=Color.red()))

        logs = channel[0]


        await ctx.author.edit(nick=nickname)
        await ctx.send(embed= discord.Embed(title='Nick changed.', description=f"> {ctx.author}, your nickname has been set to **{nickname}** in this server!"),color=Color.green())

        embed = discord.Embed(
        title="! MANAGENICK !",
        description=f"- 🧍 User: {ctx.author.mention}\n- 🪪 User name: {ctx.author}\n- 🪪 User Id: `{ctx.author.id}`\n- 📛 Nick: {ctx.author.nick}",
        color=Color.from_rgb(27, 152, 250),
        )

        chan = self.bot.get_channel(logs)

        await chan.send(embed=embed.set_thumbnail(url=ctx.author.avatar.url))

    @nick.error
    async def on_nick_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Nick error**', description=f'> Error: {str(error)}', color=Color.red()))


####################################################################################################################################
#################################################################################################################################### NICK END, POLL START
####################################################################################################################################

    @commands.hybrid_command(name="createpoll", description="Creates a community poll in the current channel.")
    @commands.has_permissions(manage_messages=True)
    async def createpoll(
        self,
        ctx,
        question: str,
        option1: str,
        option2: str,
        option3: str = None,
        option4: str = None,
    ) -> None:
        
        print("[Createpoll] has just been executed!")
        
        channel = ctx.channel
        await ctx.defer()

        poll = discord.Embed(
            title=f"\n> {question}",
            color=Color.from_rgb(27, 152, 250),
        )
        try:
            await ctx.message.delete()
        except:
            pass
        poll.add_field(name="1)", value=option1, inline=True)
        poll.add_field(name="2)", value=option2, inline=True)
        if option3 != None:
            poll.add_field(name="3)", value=option3, inline=True)
        if option4 != None:
            poll.add_field(name="4)", value=option4, inline=True)

        msg = await channel.send(embed=poll, content="||@everyone||")
        await ctx.send(embed=discord.Embed(description='✅ Poll created.', color=Color.green()), delete_after=5.0)

        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        if option3 != None:
            await msg.add_reaction("3️⃣")
        if option4 != None:
            await msg.add_reaction("4️⃣")

    @createpoll.error
    async def on_createpoll_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Createpoll error**', description=f'> Error: {str(error)}', color=Color.red()))

####################################################################################################################################
#################################################################################################################################### POLL END, USERINFO START
####################################################################################################################################

    @commands.hybrid_command(
        name="userinfo", description="Returns a information about the passed user."
    )
    async def userinfo(
        self, ctx, member: discord.Member = None
    ):
        try:
            await ctx.message.delete()
        except:
            pass
        
        print("[Userinfo] has just been executed.")
        await ctx.defer()

        msg = await ctx.send(embed=discord.Embed(description="Gathering info...", color=Color.yellow()))

        if not member:
            member = ctx.author

   #     time_format = "%a, %d/%b/%Y"

        timestamp1 = discord.utils.format_dt(member.created_at, style="F")
        timestamp2 = discord.utils.format_dt(member.joined_at, style="F")

        rolelist = [
            r.mention for r in member.roles if r != ctx.guild.default_role
        ]
        rolenum = 0
        for i in member.roles:
            rolenum += 1

        ############################################################################# BADGES

        badges = []
        if member.public_flags.active_developer:
            badges.append("<:activedev:1132730402629500988>")
        if member.public_flags.bug_hunter:
            badges.append("<:bughunter:1132444448341626943>")
        if member.public_flags.bug_hunter_level_2:
            badges.append("<:bughuntergold:1132444426774519828>")
        if member.public_flags.discord_certified_moderator:
            badges.append("<:verifiedmoderator:1132444404548894810>")
        if member.public_flags.early_supporter:
            badges.append("<:earlysupporter:1132446776796913674>")
        if member.public_flags.early_verified_bot_developer:
            badges.append("<:earlybotdev:1132447312350826496>")
        if member.public_flags.hypesquad_balance:
            badges.append("<:hypesquadbalance:1132447780087021598>")
        if member.public_flags.hypesquad_bravery:
            badges.append("<:hypesquadbravery:1132444545246830602>")
        if member.public_flags.hypesquad_brilliance:
            badges.append("<:hypesquadbrilliance:1132448075969998908>")
        if member.public_flags.partner:
            badges.append("<:partner:1132444469476732958>")
        if member.public_flags.staff:
            badges.append("<:staff:1132444489273852024>")

        def guess_user_nitro_status(user: discord.Member):
            if isinstance(user, discord.Member):
                has_emote_status = any(
                    [
                        a.emoji.is_custom_emoji()
                        for a in user.activities
                        if getattr(a, "emoji", None)
                    ]
                )

                return any(
                    [
                        user.display_avatar.is_animated(),
                        has_emote_status,
                        user.premium_since,
                        user.guild_avatar,
                    ]
                )

            return any([user.display_avatar.is_animated(), user.banner])

        if guess_user_nitro_status(member):
            badges.append("<:nitro:1132456899888037948>")

        badgecount = 0
        for i in badges:
            badgecount += 1

        ############################################################################# END BADGES


        description  =  [f'- 🧍 User: {member.mention}',
                        f'- 🪪 User name: {member}',
                        f'- 🪪 User Id: `{member.id}`', f'- 📛 Nickname: {member.nick}',
                        f'- 🤖 Bot: {member.bot}', f'- 📆 Account created: {timestamp1}', 
                        f'- 📆 Joined at: {timestamp2}', 
                        f'- 🔸 Discord badges ({badgecount}): {", ".join(badges) if badges else "No badges"}', 
                        f'- 🔸 Roles ({rolenum-1}): {", ".join(rolelist) if rolelist else "No roles"}']



        if member.is_timed_out():
            timestamp3 = discord.utils.format_dt(member.timed_out_until, style="F")
            description.append(f'- ⏰ Is timed out: {member.is_timed_out()}')
            description.append(f'- ⏰ Timed out until: {timestamp3}')


        info = discord.Embed(
            title=f"{member}",
            description='\n'.join(description),
            color=Color.green(),
        )

        await msg.edit(
            embed=info.set_thumbnail(url=member.avatar.url),
        )

    @userinfo.error
    async def on_userinfo_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Userinfo error**', description=f'> Error: {str(error)}', color=Color.red()))

####################################################################################################################################
#################################################################################################################################### USERINFO END, TRUTH OR DARE START
####################################################################################################################################

    @commands.hybrid_command(name="truth", description="Gives you a random truth.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def truth(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.defer()
        print("[Truth] has just been executed")
        embed = discord.Embed(
            title="! **• Truth •** !",
            description=f"\n- First choice: {random.choice(truth)}\n- Second choice: {random.choice(truth)}\n*Choose wisely*",
            color=Color.green(),
        )
        embed.set_footer(text=f"Answer truthfully...")

        await ctx.send(embed=embed)

    @truth.error
    async def on_truth_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Truth error**', description=f'> Error: {str(error)}', color=Color.red()))

    @app_commands.command(name="dare", description="Gives you a random dare.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def dare(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.defer()
        print("[Dare] has just been executed")

        embed = discord.Embed(
            title="Dare chosen.",
            description=f"> First choice: {random.choice(dare)}\n> Second choice: {random.choice(dare)}\n*Choose wisely*",
            color=Color.green(),
        ),embed.set_footer(text=f"Just do it!")

        await ctx.send(embed=embed)

    @dare.error
    async def on_dare_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Dare error**', description=f'> Error: {str(error)}', color=Color.red()))


####################################################################################################################################
#################################################################################################################################### TRUTH OR DARE END GIVEAWAY BEGIN
####################################################################################################################################

#    @app_commands.command(name='giveaway', description='Creates a giveaway!')
 #   @app_commands.default_permissions(administrator=True)
  #  async def create_giveaway(self, interaction:discord.Interaction,title:str,description:str,winnings:str, time:Literal['10m', '20m', '30m', '1h', '6h', '12h']):
   #     await interaction.response.defer(ephemeral=True)
    #    global time2
     #   time2 = time
      #  global meeswage
       # meeswage = await interaction.followup.send(embed=discord.Embed(title=f'# **{title}**', description=f'{description}\n \n> Time: {time}\n> Users joined: {users_joined}'),view=Join())



#class Join(View):
 #   def __init__(self):
  #      super().__init__(timeout=None)
   # 
    #@button(label='Join giveaway', style=discord.ButtonStyle.blurple, custom_id='persistent:joingiveaway', emoji='🎉')
    #async def joingiveaway(self, interaction:discord.Interaction, button:Button):
     #   await interaction.response.defer(ephemeral=True)

      #  msg = await interaction.followup.send(embed=discord.Embed(title='**Joining giveaway**', description='> You are being added to the giveaway!', color=Color.yellow()), ephemeral=True)

       # giveaway_users.append(interaction.user.id)
        #print(giveaway_users)
       # print(users_joined)
        #await meeswage.edit(embed=discord.Embed(description=f'{Community.create_giveaway.description}\n \n> Time: {time2}\n> Users joined: {users_joined}'))

        #await msg.edit(embed=discord.Embed(title='**Giveaway joined**', description='> You were added to the giveaway!', color=Color.green()))


####################################################################################################################################
#################################################################################################################################### GIVEAWAY END TAGS BEGIN
####################################################################################################################################


    @commands.hybrid_command(name='createtag', description='Creates a tag to be used in the current guild.')
    @commands.has_permissions(manage_messages=True)
    async def create_tag(self, ctx, tag_name:str, tag_info:str):
        await ctx.defer()

        msg = await ctx.send(embed=discord.Embed(title="**Creating tag...**", description=f"\n> Tag name: {tag_name}\n> Tag info: {tag_info}", color=Color.yellow()))

        db = await aiosqlite.connect("tags.db")

        await db.execute("""CREATE TABLE IF NOT EXISTS tags(guild_name, guild_id, tag_name, tag_info)""")


        cur = await db.execute("""SELECT tag_name FROM tags WHERE guild_id = ?""", (ctx.guild.id, ))
        res = await cur.fetchall()
        if res is not None:

            for name in res:
                if name[0].lower() == tag_name[0].lower():
                    await msg.edit(embed=discord.Embed(title='**Tag error**', description="> Error: `Tag already exists`", color=Color.red()))
                    return

        await db.execute("""INSERT INTO tags(guild_name, guild_id, tag_name, tag_info) VALUES (?,?,?,?)""", (ctx.guild.name, ctx.guild.id, tag_name.lower(), tag_info, ))
        await db.commit()

        await msg.edit(embed=discord.Embed(title='**Created tag!**', description=f'> Tag name: {tag_name}\n> Tag info: {tag_info}', color=Color.green()))
    
    @create_tag.error
    async def on_create_tag_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Createtag error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='edittag', description='Edits a tag that is already in the database.')
    @commands.has_permissions(manage_messages=True)
    async def edit_tag(self, ctx, tag_name:str, new_tag_name:str=None, new_tag_info:str=None):
        await ctx.defer()

        msg = await ctx.send(embed=discord.Embed(title="**Editing tag...**", description=f"\n> Tag name: {tag_name}", color=Color.yellow()))

        db = await aiosqlite.connect("tags.db")

        await db.execute("""CREATE TABLE IF NOT EXISTS tags(guild_name, guild_id, tag_name, tag_info)""")

        cur = await db.execute("""SELECT * FROM tags WHERE guild_id = ?""", (ctx.guild.id, ))
        res = await cur.fetchone()

        if res is None:
            await msg.edit(embed=discord.Embed(title='**Tag error**', description='> Error: `No tags found`', color=Color.red()))
            return
        
        if new_tag_info is None and new_tag_name is None:
            await msg.edit(embed=discord.Embed(title='**Tag error**', description='> Error: `You must update at least the tag name or info`.', color=Color.red()))
            return
        if new_tag_info is not None:
            await db.execute("""UPDATE tags SET tag_info = ? WHERE tag_name = ? AND guild_id = ?""", (new_tag_info.lower(), tag_name.lower(), ctx.guild.id, ))
            await db.commit()
        if new_tag_name is not None:
            await db.execute("""UPDATE tags SET tag_name = ? WHERE tag_name = ? AND guild_id = ?""", (new_tag_name.lower(), tag_name.lower(), ctx.guild.id, ))
            await db.commit()
            
        await ctx.send(embed=discord.Embed(title='**Edited tag!**', description=f'> Tag name: {new_tag_name}\n> Tag info: {new_tag_info}', color=Color.green()))
    
    @edit_tag.error
    async def on_edit_tag_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Edittag error**', description=f'> Error: {str(error)}', color=Color.red()))

##### TAG EDIT


    @commands.hybrid_command(name='tags', description='Gives lists all tags in the database.')
    async def list_tags(self, ctx):
        await ctx.defer()

        db = await aiosqlite.connect("tags.db")

        cur = await db.execute("""SELECT tag_name FROM tags WHERE guild_id = ?""", (ctx.guild.id, ))

        ress = await cur.fetchall()
        res = ress[0]

        if res is None:
            await ctx.send(embed=discord.Embed(title='**Tag error**', description="> Error: `No tags found`", color=Color.red()))
            return

        await ctx.send(embed=discord.Embed(title=f'**Tags for {ctx.guild.name}**', description='\n'.join(f"> /tag `{name[0]}`" for name in res), color=Color.blurple()))

    @list_tags.error
    async def on_list_tags_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Tags error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='deletetag', description='Deletes a tag from the database.')
    @commands.has_permissions(manage_messages=True)
    async def delete_tag(self,ctx, tag_name:str):
        await ctx.defer()

        msg = await ctx.send(embed=discord.Embed(title="**Deleting tag...**", description=f"\n> Tag name: {tag_name}", color=Color.yellow()))

        db = await aiosqlite.connect("tags.db")

        cur = await db.execute("""SELECT tag_name FROM tags WHERE guild_id = ?""", (ctx.guild.id, ))

        ress = await cur.fetchall()
        res = ress[0]

        if res is None:
            await msg.edit(embed=discord.Embed(title='**Tag error**', description="> Error: `No tags found`", color=Color.red()))
            return
        for name in res:
            if tag_name.lower() == name[0].lower():

                await db.execute("""DELETE FROM tags WHERE tag_name = ?""", (tag_name.lower(), ))
                await db.commit()

                await msg.edit(embed=discord.Embed(title=f'**Tag deleted**', description=f'> Deleted tag: {tag_name}', color=Color.green()))
                return
            else:
                await msg.edit(embed=discord.Embed(title='**Tag error**', description=f'> Error: `Tag "{tag_name}" not found.`', color=Color.red()))

    @delete_tag.error
    async def on_delete_tag_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Deletetag error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='tag', description='Fetches a tag from the database.')
    async def fetch_tag(self, ctx, tag_name:str):
        await ctx.defer()

        db = await aiosqlite.connect("tags.db")

        cur = await db.execute("""SELECT tag_name FROM tags WHERE guild_id = ?""", (ctx.guild.id, ))

        ress = await cur.fetchall()
        res = ress[0]

        if res is None:
            await ctx.send(embed=discord.Embed(title='**Tag error**', description="> Error: `No tags found`", color=Color.red()))
            return
        for name in res:
            if tag_name.lower() == name[0].lower():
                cur = await db.execute("""SELECT tag_info FROM tags WHERE tag_name = ?""", (tag_name.lower(), ))

                res = await cur.fetchone()
                await ctx.send(embed=discord.Embed(title=f'{name[0].capitalize()}', description=f'{res[0]}', color=Color.blurple()))
                return
            else:
                await ctx.send(embed=discord.Embed(title='**Tag error**', description=f'> Error: `Tag "{tag_name}" not found.`', color=Color.red()))
    @fetch_tag.error
    async def on_fetch_tag_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Fetchtag error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='givesaves', description='Gives saves for the counting feature to a user.')
    @commands.has_permissions(moderate_members=True)
    async def give_saves(self, ctx, member:discord.Member, saves:int):
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.defer()

        db = await aiosqlite.connect('counting.db')
        await db.execute("""CREATE TABLE IF NOT EXISTS saves(guild_name TEXT, guild_id INTEGER,user INTEGER, saves INTEGER)""")


        cur = await db.execute("""SELECT user FROM saves WHERE guild_id = ? AND user = ?""", (ctx.guild.id, member.id, ))
        res = cur.fetchone()

        cur2 = await db.execute("""SELECT saves FROM saves WHERE guild_id = ? AND user = ?""", (ctx.guild.id, member.id, ))
        res2 = await cur2.fetchone()

        if res2[0] is not None:prev_saves = res2[0]
        else: prev_saves = None
        new_saves = prev_saves + saves

        if res is None:

            await db.execute("""INSERT INTO saves (guild_name, guild_id, user, saves) VALUES(?,?,?,?)""", (ctx.guild.name, ctx.guild.id, member.id, new_saves,  ))
            await db.commit()
        if res is not None:

            await db.execute("""UPDATE saves SET saves = ? WHERE guild_id =? AND user = ?""", (new_saves, ctx.guild.id, member.id, ))
            await db.commit()
        await ctx.send(embed=discord.Embed(title='**Give saves**', description=f'> User: {member.mention}\n> Old saves: {prev_saves}\n New saves: {new_saves}', color=Color.green()))
            
    @give_saves.error
    async def on_give_saves_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Givesaves error**', description=f'> Error: {str(error)}', color=Color.red()))


    @app_commands.command(name='setsaves', description='Sets saves for the counting feature for a user')
    @app_commands.default_permissions(administrator=True)
    async def set_saves(self, ctx, member:discord.Member, saves:int):
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.defer()

        db = await aiosqlite.connect('counting.db')
        await db.execute("""CREATE TABLE IF NOT EXISTS saves(guild_name TEXT, guild_id INTEGER,user INTEGER, saves INTEGER)""")


        cur = await db.execute("""SELECT user FROM saves WHERE guild_id = ? AND user = ?""", (ctx.guild.id, member.id, ))
        res = await cur.fetchone()

        cur2 = await db.execute("""SELECT saves FROM saves WHERE guild_id = ? AND user = ?""", (ctx.guild.id, member.id, ))
        res2 = await cur2.fetchone()

        if res2 is not None: 
            prev_saves = res2[0]
        else: prev_saves = None

        new_saves = saves

        if res is None:

            await db.execute("""INSERT INTO saves (guild_name, guild_id, user, saves) VALUES(?,?,?,?)""", (ctx.guild.name, ctx.guild.id, member.id, new_saves,  ))
            await db.commit()
        if res is not None:

            await db.execute("""UPDATE saves SET saves = ? WHERE guild_id =? AND user = ?""", (new_saves, ctx.guild.id, member.id, ))
            await db.commit()
        await ctx.send(embed=discord.Embed(title='**Set saves**', description=f'> User: {member.mention}\n> Old saves: {prev_saves}\n New saves: {saves}', color=Color.green()))
            
    @set_saves.error
    async def on_set_saves_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Setsaves error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='removesaves', description='Gives saves for the counting feature to a user.')
    @commands.has_permissions(moderate_members=True)
    async def remove_saves(self, ctx, member:discord.Member, saves:int):
        try:
            await ctx.message.delete()
        except:
            pass
        await ctx.defer()

        db = await aiosqlite.connect('counting.db')
        await db.execute("""CREATE TABLE IF NOT EXISTS saves(guild_name TEXT, guild_id INTEGER,user INTEGER, saves INTEGER)""")


        cur = await db.execute("""SELECT user FROM saves WHERE guild_id = ? AND user = ?""", (ctx.guild.id, member.id, ))
        res = await cur.fetchone()

        cur2 = await db.execute("""SELECT saves FROM saves WHERE guild_id = ? AND user = ?""", (ctx.guild.id, member.id, ))
        res2 = await cur2.fetchone()

        if res2 is not None: prev_saves = res2[0]
        else: prev_saves = None
        new_saves = prev_saves - saves

        if new_saves < 0:
            new_saves = 0

        if res is None:

            await db.execute("""INSERT INTO saves (guild_name, guild_id, user, saves) VALUES(?,?,?,?)""", (ctx.guild.name, ctx.guild.id, member.id, new_saves,  ))
            await db.commit()
        if res is not None:

            await db.execute("""UPDATE saves SET saves = ? WHERE guild_id =? AND user = ?""", (new_saves, ctx.guild.id, member.id, ))
            await db.commit()
        await ctx.send(embed=discord.Embed(title='**Remove saves**', description=f'> User: {member.mention}\n> Old saves: {prev_saves}\n New saves: {new_saves}', color=Color.green()))

    @remove_saves.error
    async def on_remove_saves_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Removesaves error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='saves', description='Tells you your amount of saves.')
    async def saves(self, ctx, member:discord.Member=None):
        await ctx.defer()

        if member == None:
            member = ctx.author

        db = await aiosqlite.connect('counting.db')
        await db.execute("""CREATE TABLE IF NOT EXISTS saves(guild_name TEXT,user INTEGER, saves INTEGER)""")


        cur = await db.execute("""SELECT user, saves FROM saves WHERE guild_id = ? AND user = ?""", (ctx.guild.id, member.id, ))
        res = await cur.fetchone()

        if res is None:
            await ctx.send(embed=discord.Embed(title='**Saves error**', description='> Error: You were not found in the database.', color=Color.red()))
            return
        if res is not None:
            await ctx.send(embed=discord.Embed(title='**Saves**', description=f'> Saves: {res[1]}', color=Color.green()))
            return

    @saves.error
    async def on_saves_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Saves error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='genkey', description='Creates an API key.')
    @commands.has_permissions(administrator=True)
    async def genkey(self, ctx):
        msg = await ctx.send(embed=discord.Embed(description='<:yellowdot:1148198566448337018> Generating Key.', color=Color.yellow()))
        sec1 = random.choice(chars) + random.choice(chars) + random.choice(chars) + random.choice(chars)
        sec2 = random.choice(chars) + random.choice(chars) + random.choice(chars) + random.choice(chars)
        sec3 = random.choice(chars) + random.choice(chars) + random.choice(chars) + random.choice(chars)
        key = f'{sec1}{seperator}{sec2}{seperator}{sec3}'

        db = await aiosqlite.connect("keys.db")
        await db.execute("CREATE TABLE IF NOT EXISTS keys(guild_name STRING, key STRING, activated STRING)")

        await db.execute("INSERT INTO keys(guild_name, key, activated) VALUES(?,?,?)", (ctx.guild.name, key, 'False', ))
        await db.commit()


        await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Key Generated: `{key}`', color=Color.green()))

    @genkey.error
    async def on_genkey_error(
        self, ctx, error
    ):
        await ctx.send(embed=discord.Embed(title='**Genkey error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='activatekey', description='Activates an API key.')
    @commands.cooldown(1,15, commands.BucketType.user)
    async def activatekey(self, ctx, key:str):
        msg = await ctx.send(embed=discord.Embed(description='<:yellowdot:1148198566448337018> Activating Key.', color=Color.yellow()))
        db = await aiosqlite.connect("keys.db")
        cur = await db.execute("SELECT key, activated FROM keys WHERE key = ?", (key, ))
        res = await cur.fetchall()
        res1 = res[0]
        if res[0] is None:
            await msg.edit(embed=discord.Embed(description='<:redtick:1148198569296273408> Invalid Key.', color=Color.red()))
            return
        if res1[1] == 'True':
            await msg.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Key already active.', color=Color.red()))
            return
        await db.execute("UPDATE keys SET activated = ? WHERE key = ?", ('True', key, ))
        await db.commit()
        await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Activated Key.', color=Color.green()))

    @activatekey.error
    async def on_activatekey_error(
        self, ctx, error
    ):
        await ctx.send(embed=discord.Embed(title='**Activatekey error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='disablekey', description='Disables an API key.')
    @commands.cooldown(1,15, commands.BucketType.user)
    async def disablekey(self, ctx, key:str):
        msg = await ctx.send(embed=discord.Embed(description='<:yellowdot:1148198566448337018> Disabling Key.', color=Color.yellow()))
        db = await aiosqlite.connect("keys.db")
        cur = await db.execute("SELECT key, activated FROM keys WHERE key = ?", (key, ))
        res = await cur.fetchall()
        res1 = res[0]
        if res1 is None:
            await msg.edit(embed=discord.Embed(description='<:redtick:1148198569296273408> Invalid Key.', color=Color.red()))
            return
        if res1[1] == 'False':
            await msg.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Key not active.', color=Color.red()))
            return
        await db.execute("UPDATE keys SET activated = ? WHERE key = ?", ('False', key, ))
        await db.commit()
        await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Key Disabled.', color=Color.green()))

    @disablekey.error
    async def on_disablekey_error(
        self, ctx, error
    ):
        await ctx.send(embed=discord.Embed(title='**Disablekey error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='deletekey', description='Disables an API key.')
    @commands.has_permissions(administrator=True)
    @commands.cooldown(1,15, commands.BucketType.user)
    async def deletekey(self, ctx, key:str):
        await ctx.message.delete()
        code = random.choice(chars) + random.choice(chars) + random.choice(chars)
        conf = await ctx.send(embed=discord.Embed(description=f'<:yellowdot:1148198566448337018> Confirmation code: `{code}`', color=Color.yellow()).set_footer(text='*Send the code within ten seconds!*'))

        def check(m):
            return m.author == ctx.author and m.content == f'{code}' and m.channel == ctx.channel
        try:
            m = await self.bot.wait_for('message', check=check, timeout=10.0)
        except asyncio.TimeoutError:
            await conf.edit(embed=discord.Embed(description='<:redtick:1148198569296273408> Code not sent fast enough.', color=Color.red()))
            await asyncio.sleep(5)
            await conf.delete()
            return
        else:
            await conf.edit(embed=discord.Embed(description='<:yellowdot:1148198566448337018> Deleting key.', color=Color.yellow()))
            db = await aiosqlite.connect("keys.db")
            cur = await db.execute("SELECT key, activated FROM keys WHERE key = ?", (key, ))
            res = await cur.fetchall()
            res1 = res[0]
            if res1 is None:
                await conf.edit(embed=discord.Embed(description='<:redtick:1148198569296273408> Invalid Key.', color=Color.red()))
                return
            await db.execute("DELETE FROM keys WHERE key = ?", (key, ))
            await db.commit()
            await conf.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Key deleted.', color=Color.green()))

    @deletekey.error
    async def on_deletekey_error(
        self, ctx, error
    ):
        await ctx.send(embed=discord.Embed(title='**Deletekey error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='keys', description='Lists all API keys.')
    @commands.cooldown(1,15, commands.BucketType.user)
    async def keys(self, ctx):
        msg = await ctx.send(embed=discord.Embed(description='🔑 Fetching keys...', color=Color.yellow()))
        db = await aiosqlite.connect("keys.db")
        cur = await db.execute("SELECT key, activated FROM keys ")
        res = await cur.fetchall()
        if res[0] is None:
            await msg.edit(embed=discord.Embed(description='<:redtick:1148198569296273408> No keys found.', color=Color.red()))
            return

        key_list = []
        for key, activated in res:
            key_list.append(f"`{key}` | {activated}")

        key_pairs = '\n> '.join(key_list)

        await msg.edit(embed=discord.Embed(title='Fetched keys.', description=f'Format: KEY | ACTIVATION STATUS\n​\n> {key_pairs}', color=Color.green()))

    @keys.error
    async def on_keys_error(
        self, ctx, error
    ):
        await ctx.send(embed=discord.Embed(title='**Keys error**', description=f'> Error: {str(error)}', color=Color.red()))




async def setup(bot):
    await bot.add_cog(Community(bot))
