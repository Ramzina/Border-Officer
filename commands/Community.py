import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button,button, View
import random
from TOD.dare import dare
from TOD.truth import truth
from typing import Literal
from discord.app_commands import AppCommandError
from discord import Color
from datetime import datetime
import aiosqlite

class Community(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

####################################################################################################################################
#################################################################################################################################### NICK START
####################################################################################################################################

    @app_commands.command(name="nick", description="Changes your nickname.")
    @app_commands.default_permissions(change_nickname=True)
    async def nick(self, interaction: discord.Interaction, nickname: str = None):
        print("[Nick] has just been executed!")
        await interaction.response.defer(ephemeral=True, thinking=True)


        db = await aiosqlite.connect("config.db")


        await db.execute(
            """CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
        )
        res = await db.execute(
            f"""SELECT * FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        row = await res.fetchone()
        if row is None:
            await interaction.followup.send(f'{interaction.user.mention}, To setup {self.bot.user}\'s commands properly, run /logs to set a commands log channel')
            
        res = await db.execute(
            f"""SELECT channel_id FROM logs WHERE guild_id = {interaction.guild.id}"""
        )
        channel = await res.fetchone()
        logs = channel[0]


        await interaction.user.edit(nick=nickname)
        await interaction.followup.send(
            f"{interaction.user}, your nickname has been set to **{nickname}** in this server!"
        )

        embed = discord.Embed(
        title="! MANAGENICK !",
        description=f"- 🧍 User: {interaction.user.mention}\n- 🪪 User name: {interaction.user}\n- 🪪 User Id: `{interaction.user.id}`\n- 📛 Nick: {interaction.user.nick}",
        timestamp=datetime.utcnow(),
        color=Color.from_rgb(27, 152, 250),
        )

        chan = self.bot.get_channel(logs)

        await chan.send(embed=embed.set_thumbnail(url=interaction.user.avatar.url))

    @nick.error
    async def on_nick_error(self, interaction: discord.Interaction, error):
        await interaction.followup.send(content=str(error), ephemeral=True)


####################################################################################################################################
#################################################################################################################################### NICK END, POLL START
####################################################################################################################################

    @app_commands.command(name="createpoll", description="Creates a community poll in the current channel.")
    @app_commands.default_permissions(administrator=True)
    async def createpoll(
        self,
        interaction: discord.Interaction,
        description: str,
        option1: str,
        option2: str,
        option3: str = None,
        option4: str = None,
    ) -> None:
        print("[Createpoll] has just been executed!")
        channel = interaction.channel

        await interaction.response.defer(ephemeral=True, thinking=True)

        poll = discord.Embed(
            title="! __POLL__ !",
            description="\n" + description,
            timestamp=datetime.utcnow(),
            color=Color.from_rgb(27, 152, 250),
        )
        poll.add_field(name="1)", value=option1, inline=True)
        poll.add_field(name="2)", value=option2, inline=True)
        if option3 != None:
            poll.add_field(name="3)", value=option3, inline=True)
        if option4 != None:
            poll.add_field(name="4)", value=option4, inline=True)

        msg = await channel.send(embed=poll, content="||@everyone||")
        await interaction.followup.send("Created poll!")

        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        if option3 != None:
            await msg.add_reaction("3️⃣")
        if option4 != None:
            await msg.add_reaction("4️⃣")


####################################################################################################################################
#################################################################################################################################### POLL END, USERINFO START
####################################################################################################################################

    @app_commands.command(
        name="userinfo", description="Returns a information about the passed user."
    )
    async def userinfo(
        self, interaction: discord.Interaction, member: discord.Member = None
    ):
        print("[Userinfo] has just been executed.")
        await interaction.response.defer(ephemeral=True, thinking=True)

        if not member:
            member = interaction.user

   #     time_format = "%a, %d/%b/%Y"

        timestamp1 = discord.utils.format_dt(member.created_at, style="F")
        timestamp2 = discord.utils.format_dt(member.joined_at, style="F")

        rolelist = [
            r.mention for r in member.roles if r != interaction.guild.default_role
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
                        f'- 🔸 Roles ({rolenum-1}): {", ".join(rolelist) if rolelist else "No roles"}', 
                        f'- ⏰ Is timed out: {member.is_timed_out()}']



        if member.is_timed_out():
            timestamp3 = discord.utils.format_dt(member.timed_out_until, style="F")
            description.append(f'- ⏰ Timed out until: {timestamp3}')


        info = discord.Embed(
            title=f"{member}",
            description='\n'.join(description),
            timestamp=datetime.utcnow(),
            color=Color.from_rgb(27, 152, 250),
        )

        await interaction.followup.send(
            embed=info.set_thumbnail(url=member.avatar.url), ephemeral=True
        )


####################################################################################################################################
#################################################################################################################################### USERINFO END, TRUTH OR DARE START
####################################################################################################################################

    @app_commands.command(name="truth", description="Gives you a random truth.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def truth(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        print("[Truth] has just been executed")
        embed = discord.Embed(
            title="! **• Truth •** !",
            description=f"\n- First choice: {random.choice(truth)}\n- Second choice: {random.choice(truth)}\n*Choose wisely*",
            timestamp=datetime.utcnow(),
            color=Color.from_rgb(27, 152, 250),
        )
        embed.set_footer(text=f"Answer truthfully!")

        await interaction.followup.send(
            embed=embed.set_thumbnail(url=interaction.user.avatar.url), ephemeral=True
        )

    @truth.error
    async def on_truth_error(
        self, interaction: discord.Interaction, error: AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.followup.send(content=str(error), ephemeral=True)

    @app_commands.command(name="dare", description="Gives you a random dare.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
    async def dare(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)
        print("[Dare] has just been executed")

        embed = discord.Embed(
            title="! **• Dare •** !",
            description=f"- First choice: {random.choice(dare)}\n- Second choice: {random.choice(dare)}\n*Choose wisely*",
            timestamp=datetime.utcnow(),
            color=Color.from_rgb(27, 152, 250),
        ),embed.set_footer(text=f"You better do it!")

        await interaction.followup.send(
            embed=embed.set_thumbnail(url=interaction.user.avatar.url)
        )

    @dare.error
    async def on_dare_error(
        self, interaction: discord.Interaction, error: AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.followup.send(content=str(error), ephemeral=True)


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


    @app_commands.command(name='tag-create', description='Creates a tag to be used in the current guild.')
    @app_commands.default_permissions(administrator=True)
    @app_commands.describe(tag_name='The name of the tag you are creating.', tag_info='The info of the tag you are creating.')
    async def create_tag(self, interaction:discord.Interaction, tag_name:str, tag_info:str):
        await interaction.response.defer(ephemeral=True, thinking=True)

        await interaction.followup.send(embed=discord.Embed(title="**Creating tag...**", description=f"\n> Tag name: {tag_name}\n> Tag info: {tag_info}", color=Color.yellow()),ephemeral=True)

        db = await aiosqlite.connect("tags.db")

        await db.execute("""CREATE TABLE IF NOT EXISTS tags(guild_name, guild_id, tag_name, tag_info)""")

        cur = await db.execute("""SELECT * FROM tags WHERE guild_id = ?""", (interaction.guild.id, ))
        res = await cur.fetchone()
        if res is not None:
            cur = await db.execute("""SELECT tag_name FROM tags WHERE guild_id = ?""", (interaction.guild.id, ))
            res = await cur.fetchall()

            for name in res:
                if name[0].lower() == tag_name[0].lower():
                    await interaction.edit_original_response(embed=discord.Embed(title='**Tag error**', description="> Error: `Tag already exists`", color=Color.red()))
                    return

        await db.execute("""INSERT INTO tags(guild_name, guild_id, tag_name, tag_info) VALUES (?,?,?,?)""", (interaction.guild.name, interaction.guild.id, tag_name.lower(), tag_info, ))
        await db.commit()

        await interaction.edit_original_response(embed=discord.Embed(title='**Created tag!**', description=f'> Tag name: {tag_name}\n> Tag info: {tag_info}', color=Color.green()))
    


    @app_commands.command(name='tag-edit', description='Edits a tag that is already in the database.')
    @app_commands.default_permissions(administrator=True)
    async def edit_tag(self, interaction:discord.Interaction, tag_name:str, new_tag_name:str=None, new_tag_info:str=None):
        await interaction.response.defer(ephemeral=True, thinking=True)

        await interaction.followup.send(embed=discord.Embed(title="**Editing tag...**", description=f"\n> Tag name: {tag_name}", color=Color.yellow()),ephemeral=True)

        db = await aiosqlite.connect("tags.db")

        await db.execute("""CREATE TABLE IF NOT EXISTS tags(guild_name, guild_id, tag_name, tag_info)""")

        cur = await db.execute("""SELECT * FROM tags WHERE guild_id = ?""", (interaction.guild.id, ))
        res = await cur.fetchone()

        if res is None:
            await interaction.edit_original_response(embed=discord.Embed(title='**Tag error**', description='> Error: `No tags found`', color=Color.red()))
            return
        
        if new_tag_info is None and new_tag_name is None:
            await interaction.edit_original_response(embed=discord.Embed(title='**Tag error**', description='> Error: `You must update at least the tag name or info`.', color=Color.red()))
            return
        if new_tag_info is not None:
            await db.execute("""UPDATE tags SET tag_info = ? WHERE tag_name = ? AND guild_id = ?""", (new_tag_info.lower(), tag_name.lower(), interaction.guild.id, ))
            await db.commit()
            print("num2")
        if new_tag_name is not None:
            await db.execute("""UPDATE tags SET tag_name = ? WHERE tag_name = ? AND guild_id = ?""", (new_tag_name.lower(), tag_name.lower(), interaction.guild.id, ))
            await db.commit()
            print("num1")


        await interaction.edit_original_response(embed=discord.Embed(title='**Edited tag!**', description=f'> Tag name: {new_tag_name}\n> Tag info: {new_tag_info}', color=Color.green()))
    

##### TAG EDIT


    @app_commands.command(name='tags', description='Gives lists all tags in the database.')
    async def list_tags(self, interaction:discord.Interaction):
        await interaction.response.defer(ephemeral=True, thinking=True)

        db = await aiosqlite.connect("tags.db")

        cur = await db.execute("""SELECT tag_name FROM tags WHERE guild_id = ?""", (interaction.guild.id, ))

        ress = await cur.fetchall()
        res = tuple(ress)
        print(res)

        if res is None:
            await interaction.followup.send(embed=discord.Embed(title='**Tag error**', description="> Error: `No tags found`", color=Color.red()), ephemeral=True)
            return

        await interaction.followup.send(embed=discord.Embed(title=f'**Tags for {interaction.guild.name}**', description='\n'.join(f"> /tag `{name[0]}`" for name in res), color=Color.blurple()))

    @app_commands.command(name='tag-delete', description='Deletes a tag from the database.')
    @app_commands.describe(tag_name='The name of the tag you want to delete.')
    async def delete_tag(self,interaction:discord.Interaction, tag_name:str):
        await interaction.response.defer(ephemeral=True, thinking=True)

        await interaction.followup.send(embed=discord.Embed(title="**Deleting tag...**", description=f"\n> Tag name: {tag_name}", color=Color.yellow()),ephemeral=True)

        db = await aiosqlite.connect("tags.db")

        cur = await db.execute("""SELECT tag_name FROM tags WHERE guild_id = ?""", (interaction.guild.id, ))

        res = await cur.fetchall()

        if res is None:
            await interaction.edit_original_response(embed=discord.Embed(title='**Tag error**', description="> Error: `No tags found`", color=Color.red()))
            return
        for name in res:
            if tag_name.lower() == name[0].lower():

                await db.execute("""DELETE FROM tags WHERE tag_name = ?""", (tag_name.lower(), ))
                await db.commit()

                await interaction.edit_original_response(embed=discord.Embed(title=f'**Tag deleted**', description=f'> Deleted tag: {tag_name}', color=Color.green()))
                return
            
            await interaction.edit_original_response(embed=discord.Embed(title='**Tag error**', description=f'> Error: `Tag "{tag_name}" not found.`', color=Color.red()))

    @app_commands.command(name='tag', description='Fetches a tag from the database.')
    @app_commands.describe(tag_name='The name of the tag you are fetching.')
    async def fetch_tag(self, interaction:discord.Interaction, tag_name:str, private:bool=False):
        await interaction.response.defer(ephemeral=private, thinking=True)

        db = await aiosqlite.connect("tags.db")

        cur = await db.execute("""SELECT tag_name FROM tags WHERE guild_id = ?""", (interaction.guild.id, ))

        res = await cur.fetchall()

        if res is None:
            await interaction.followup.send(embed=discord.Embed(title='**Tag error**', description="> Error: `No tags found`", color=Color.red()), ephemeral=True)
            return
        for name in res:
            if tag_name.lower() == name[0].lower():
                cur = await db.execute("""SELECT tag_info FROM tags WHERE tag_name = ?""", (tag_name.lower(), ))

                res = await cur.fetchone()
                await interaction.followup.send(embed=discord.Embed(title=f'{name[0].capitalize()}', description=f'{res[0]}', color=Color.blurple()),ephemeral=private)
                return
            
            await interaction.followup.send(embed=discord.Embed(title='**Tag error**', description=f'> Error: `Tag "{tag_name}" not found.`', color=Color.red()), ephemeral=True)


async def setup(bot):
    await bot.add_cog(Community(bot))
