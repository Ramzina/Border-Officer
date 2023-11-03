import discord
from discord import app_commands
from discord.ext import commands
from discord.interactions import Interaction
from discord.ui import Button,button, View
import random
import datetime
from TOD.dare import dare
import asyncio
from TOD.truth import truth
from typing import Literal
from discord.app_commands import AppCommandError
from discord import Color
import datetime
import aiosqlite



chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890'
seperator = '-'

time_convert = {"s": 1, "m": 60, "h": 3600, "d": 86400}
def convert_time_to_seconds(time):
    try:
        return int(time[:-1]) * time_convert[time[-1]]
    except:
        return time
import ast
def insert_returns(body):
    # insert return stmt if the last expression is a expression statement
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    # for if statements, we insert returns into the body and the orelse
    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    # for with blocks, again we insert returns into the body
    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)



class NitroRedeem(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label='ㅤㅤㅤㅤㅤㅤRedeem!ㅤㅤㅤㅤㅤㅤ', style=discord.ButtonStyle.green, custom_id='nitroaccept')
    async def nitroaccept(self, interaction:discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)

        await interaction.followup.send(embed=discord.Embed(description=f'Get fucking trolled 😭', color=Color.red()).set_image(url='https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.kym-cdn.com%2Fphotos%2Fimages%2Fnewsfeed%2F002%2F213%2F963%2F293.jpg&f=1&nofb=1&ipt=f823b62ebc7bd23f50b1d063696aa85d006f4e2d712cf7b62ad76c4507bdf968&ipo=images'), ephemeral=True)



class FoodConfirm(View):
    def __init__(self, original_author: int, original_message: int):
        self.author = original_author
        self.message = original_message
        super().__init__(timeout=None)

    async def interaction_check(self, interaction:discord.Interaction) -> bool:
        if interaction.user.id == self.author:
            return True
        else:
            await interaction.response.send_message(ephemeral=True, embed=discord.Embed(description='This button is not for you.', color=Color.red()), view=None)
            return False

    @button(label='Confirm!', style=discord.ButtonStyle.green, custom_id='foodconfirm')
    async def confirm(self, interaction:discord.Interaction, button:Button):
        msg = await interaction.channel.fetch_message(self.message)
        await msg.edit(embed=discord.Embed(title='Food Ordered!', description='> Your food is on the way! Please wait 5 minutes.', color=Color.green()), view=None)

        await asyncio.sleep(300) # 300 = 5 minutes

        await interaction.channel.send(content=f'||{interaction.user.mention}||',embed=discord.Embed(title='Food Arrived!', description=f'> {interaction.user.name} ({interaction.user.mention}) Your food is here!', color=Color.green()))
    
    @button(label='Cancel', style=discord.ButtonStyle.danger, custom_id='foodcancel')
    async def cancel(self, interaction:discord.Interaction, button:Button):
        msg = await interaction.channel.fetch_message(self.message)

        await msg.edit(embed=discord.Embed(title='Order Cancelled!', description=f'> {interaction.user.name} ({interaction.user.mention}) cancelled the food order!', color=Color.red()).set_footer(text='Deleting order request in 5 seconds.'), view=None)

        await asyncio.sleep(5)
        
        await msg.delete()


class GiveawayJoin(View):
    def __init__(self, message_id,required_role, joined_mems, joined_list, prize, winners, start_time,time):
        self.time = time
        self.start_time = start_time
        self.message_id = message_id
        self.prize = prize
        self.winners = winners
        self.joined_list = joined_list
        self.joined = joined_mems
        self.req_role = required_role
        super().__init__(timeout=None)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if f"<@{interaction.user.id}>" in self.joined_list:
            embed=discord.Embed(description=f'You have already entered this giveaway!', color=Color.red())
            View = GiveawayLeave(self.message_id, self.req_role, self.joined, self.joined_list, self.prize, self.winners, self.start_time,self.time)
            await interaction.response.send_message(embed=embed, view=View, ephemeral=True)
            return False
        if self.req_role in interaction.user.roles or self.req_role is None:
            return True
        if self.req_role not in interaction.user.roles:
            await interaction.response.send_message(ephemeral=True, embed=discord.Embed(description=f'You don\'t have the role {self.req_role}, required to join this giveaway!', color=Color.red()))
            return False

    @button(label='Join Giveaway!', style=discord.ButtonStyle.blurple, custom_id='giveawayjoin')
    async def giveawayjoin(self, interaction:discord.Interaction, button:Button):
        await interaction.response.defer(thinking=True, ephemeral=True)

        self.joined_list.append(f"<@{interaction.user.id}>")
        self.joined += 1
        await interaction.followup.send(embed=discord.Embed(description=f'Joined giveaway! Joiner number {self.joined}', color=Color.blurple()),ephemeral=True)
        msg = await interaction.channel.fetch_message(self.message_id)
        await msg.edit(embed=discord.Embed(title=f'{self.prize.capitalize()}', description=f'> Expires: {discord.utils.format_dt(self.start_time + datetime.timedelta(0, int(self.time)), style="R")} \n> Winners: {self.winners}\n> Entries: {self.joined}\n> Required Role: {self.req_role} ', color=Color.blurple()))

class GiveawayLeave(View):
    def __init__(self, message_id,required_role, joined_mems, joined_list, prize, winners, start_time,time):
        self.time = time
        self.start_time = start_time
        self.message_id = message_id
        self.prize = prize
        self.winners = winners
        self.joined_list = joined_list
        self.joined = joined_mems
        self.req_role = required_role
        super().__init__(timeout=None)
    
    @button(label='Leave Giveaway', style=discord.ButtonStyle.danger, custom_id='giveawayleave')
    async def giveawayleave(self, interaction:discord.Interaction, button:Button):
        await interaction.response.defer(thinking=True, ephemeral=True)

        View = GiveawayJoin(self.message_id, self.req_role, self.joined, self.joined_list, self.prize, self.winners, self.start_time,self.time)

        print(self.joined_list)

        self.joined_list.remove(f"<@{interaction.user.id}>")
        self.joined -= 1

        await interaction.followup.send(embed=discord.Embed(description=f'You have exited the giveaway.', color=Color.red()),ephemeral=True)
        msg = await interaction.channel.fetch_message(self.message_id)
        await msg.edit(embed=discord.Embed(title=f'{self.prize.capitalize()}', description=f'> Expires: {discord.utils.format_dt(self.start_time + datetime.timedelta(0, int(self.time)), style="R")} \n> Winners: {self.winners}\n> Entries: {self.joined}\n> Required Role: {self.req_role} ', color=Color.blurple()))

class GiveawayReroll(View):
    def __init__(self, joined_list, winners, prize, message_id):
        self.message_id = message_id
        self.joined_list = joined_list
        self.winners = winners
        self.prize = prize
        super().__init__(timeout=None)
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        user = interaction.user.guild_permissions
        if user.administrator == True:
            return True
        else:
            await interaction.response.send_message(embed=discord.Embed(description=f'You don\'t have the required permissions to reroll this giveaway.', color=Color.red()), ephemeral=True)
            return False
        
    @button(label='Reroll Giveaway.', style=discord.ButtonStyle.danger, custom_id='giveawayreroll')
    async def giveawayreroll(self, interaction:discord.Interaction, button:Button):
        await interaction.response.defer(thinking=True)

        message = await interaction.channel.fetch_message(self.message_id)
        await message.edit(view=None)

        winner_list = random.sample(self.joined_list, self.winners)

        msg = await interaction.followup.send(embed=discord.Embed(title='Giveaway Rerolled!', description=f'> Winner\s: {", ".join(winner_list)}\n> Prize: {self.prize}', color=Color.blurple()))
        await msg.edit(view=GiveawayReroll(self.joined_list,self.winners,self.prize, msg.id))

class Community(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command(name='giveaway', description='Creates a giveaway!')
    @app_commands.default_permissions(administrator=True)
    async def giveawaycreate(self, interaction:discord.Interaction, prize:str,time:str="5m", winners:int=1, required_role:discord.Role=None):

        await interaction.response.defer(ephemeral=True, thinking=True)

        time = convert_time_to_seconds(time)
        print(time)
        start_time = discord.utils.utcnow()

        if winners <= 0:
            await interaction.response.send_message(embed=discord.Embed(title='Giveaway Error.', description='> Error: Winners amount must be greater than 0'))
            return


        joined = 0
        joined_list = []

        msg = await interaction.channel.send(embed=discord.Embed(title=f'{prize}', description=f'> Expires: {discord.utils.format_dt(start_time + datetime.timedelta(0, int(time)), style="R")} \n> Winners: {winners}\n> Entries: {joined}\n> Required Role: {required_role} ', color=Color.blurple()))
        View = GiveawayJoin(msg.id, required_role, joined, joined_list, prize, winners, start_time,time)
        await msg.edit(view=View)
        await interaction.followup.send(embed=discord.Embed(description=f'✅ Created giveaway!', color=Color.green()), ephemeral=True)

        await asyncio.sleep(time)

        winner_list = random.sample(View.joined_list, winners)

        meesg = await interaction.channel.send(embed=discord.Embed(title=f'Giveaway ended!', description=f'> Winner\s: {", ".join(winner_list)}\n> Prize: {prize}', color=Color.blurple()))
        await meesg.edit(view=GiveawayReroll(View.joined_list, winners, prize, meesg.id))


        await msg.edit(view=None)


    @commands.hybrid_command(name="orderfood", description='Order\'s you a random food! Arrives in 5 minutes.')
    @commands.cooldown(1,30, commands.BucketType.user)
    async def foodorder(self, ctx):
        await ctx.defer()

        try:
            await ctx.message.delete()
        except:
            pass

        msg = await ctx.send(embed=discord.Embed(title='Food Order!', description=f'> {ctx.author} ({ctx.author.mention}) are you sure you want to order food?', color=Color.yellow()))
        await msg.edit(view=FoodConfirm(ctx.author.id, msg.id))

    @foodorder.error
    async def on_foodorder_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='**Order Food error**', description=f'> Error: {str(error)}', color=Color.red()))


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
        option5: str = None,
        option6: str = None,
        option7: str = None,
        option8: str = None,
        option9: str = None,
        option10: str = None,
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
        if option5:
            poll.add_field(name="5)", value=option5, inline=True)

        msg = await channel.send(embed=poll, content="||@everyone||")
        await ctx.send(embed=discord.Embed(description='✅ Poll created.', color=Color.green()), delete_after=5.0)

        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        if option3 != None:
            await msg.add_reaction("3️⃣")
        if option4 != None:
            await msg.add_reaction("4️⃣")
        if option5:
            await msg.add_reaction("5️⃣")
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

    @commands.command()
    async def nitrogift(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed(title=f'**{ctx.author} gifted nitro!**',description=f'> You can claim it now by clicking redeem!\n> Expires in:  {discord.utils.format_dt(discord.utils.utcnow() + datetime.timedelta(0,60), style="R")}', color=Color.blurple()).set_thumbnail(url='https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fmedia.discordapp.net%2Fattachments%2F717627025128423502%2F719859473413570580%2Fimage0.jpg&f=1&nofb=1&ipt=a4e3db00e9d9f5caad3f0bd3742e41cc3bd07fc210058e0e93eff04e149e8c36&ipo=images')
        msg = await ctx.send(embed=embed, view=NitroRedeem())
        await asyncio.sleep(60.0)
        await msg.edit(view=None, embed=discord.Embed(title=f'**{ctx.author} Trolled you..**',description=f'> I feel bad for whoever fell for that 😭\n> Don\'t fall for this shit again 😂', color=Color.red()).set_thumbnail(url='https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fi.kym-cdn.com%2Fphotos%2Fimages%2Fnewsfeed%2F002%2F213%2F963%2F293.jpg&f=1&nofb=1&ipt=f823b62ebc7bd23f50b1d063696aa85d006f4e2d712cf7b62ad76c4507bdf968&ipo=images').set_footer(text=f'{self.bot.command_prefix}nitrogift || Get that bitch back 😏'))
    @nitrogift.error
    async def on_nitrogift_error(self, ctx, error):
        await ctx.send(embed=discord.Embed(title='NitroGift Error', description=f'> Error: {str(error)}'))

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
    async def create_tag(self, ctx, tag_name:str, *,tag_info:str):
        await ctx.defer()

        msg = await ctx.send(embed=discord.Embed(title="**Creating tag...**", description=f"\n> Tag name: {tag_name}\n> Tag info: {tag_info}", color=Color.yellow()))

        db = await aiosqlite.connect("tags.db")

        await db.execute("""CREATE TABLE IF NOT EXISTS tags(guild_name, guild_id, tag_name, tag_info)""")


        cur = await db.execute("""SELECT tag_name FROM tags WHERE guild_id = ? AND tag_name = ?""", (ctx.guild.id, tag_name, ))
        res = await cur.fetchone()
        if res:
            await msg.edit(embed=discord.Embed(title='**Tag error**', description="> Error: `Tag already exists`", color=Color.red()))
            return

        await db.execute("""INSERT INTO tags(guild_name, guild_id, tag_name, tag_info) VALUES (?,?,?,?)""", (ctx.guild.name, ctx.guild.id, tag_name.lower(), tag_info, ))
        await db.commit()

        await msg.edit(embed=discord.Embed(title='**Created tag!**', description=f'> Tag name: {tag_name}\n> Tag info: {tag_info}', color=Color.green()))
        await db.close()
#    @create_tag.error
#    async def on_create_tag_error(self, ctx, error):
#        await ctx.send(embed=discord.Embed(title='**Createtag error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='edittag', description='Edits a tag that is already in the database.')
    @commands.has_permissions(manage_messages=True)
    async def edit_tag(self, ctx, tag_name:str, new_tag_name:str=None, new_tag_info:str=None):
        await ctx.defer()

        msg = await ctx.send(embed=discord.Embed(title="**Editing tag...**", description=f"\n> Tag name: {tag_name}", color=Color.yellow()))

        db = await aiosqlite.connect("tags.db")

        await db.execute("""CREATE TABLE IF NOT EXISTS tags(guild_name, guild_id, tag_name, tag_info)""")

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
        await db.close()
#    @edit_tag.error
#    async def on_edit_tag_error(self, ctx, error):
#        await ctx.send(embed=discord.Embed(title='**Edittag error**', description=f'> Error: {str(error)}', color=Color.red()))

##### TAG EDIT


    @commands.hybrid_command(name='tags', description='Gives lists all tags in the database.')
    async def list_tags(self, ctx):
        await ctx.defer()

        db = await aiosqlite.connect("tags.db")

        cur = await db.execute("""SELECT * FROM tags WHERE guild_id = ?""", (ctx.guild.id, ))

        ress = await cur.fetchall()
        if not ress:
            await ctx.send(embed=discord.Embed(title='**Tag error**', description="> Error: `No tags found`", color=Color.red()))
            return
        res = ress[0]

        await ctx.send(embed=discord.Embed(title=f'**Tags for {ctx.guild.name}**', description='\n'.join(f"> {self.bot.command_prefix}tag `{name[2]}`" for name in ress), color=Color.blurple()))
        await db.close()
#    @list_tags.error
#    async def on_list_tags_error(self, ctx, error):
#        await ctx.send(embed=discord.Embed(title='**Tags error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='deletetag', description='Deletes a tag from the database.')
    @commands.has_permissions(manage_messages=True)
    async def delete_tag(self,ctx, tag_name:str):
        await ctx.defer()

        msg = await ctx.send(embed=discord.Embed(title="**Deleting tag...**", description=f"\n> Tag name: {tag_name}", color=Color.yellow()))

        db = await aiosqlite.connect("tags.db")

        cur = await db.execute("""SELECT tag_name FROM tags WHERE guild_id = ? AND tag_name = ?""", (ctx.guild.id, tag_name.lower(), ))

        ress = await cur.fetchone()

        if not ress:
            await msg.edit(embed=discord.Embed(title='**Tag error**', description="> Error: `No tags found`", color=Color.red()))
            return

        await db.execute("""DELETE FROM tags WHERE tag_name = ?""", (tag_name.lower(), ))
        await db.commit()

        await msg.edit(embed=discord.Embed(title=f'**Tag deleted**', description=f'> Deleted tag: {tag_name}', color=Color.green()))
        await db.close()
#    @delete_tag.error
#    async def on_delete_tag_error(self, ctx, error):
#        await ctx.send(embed=discord.Embed(title='**Deletetag error**', description=f'> Error: {str(error)}', color=Color.red()))

    @commands.hybrid_command(name='tag', description='Fetches a tag from the database.')
    async def fetch_tag(self, ctx, tag_name:str):
        await ctx.defer()

        db = await aiosqlite.connect("tags.db")

        cur = await db.execute("""SELECT tag_name, tag_info FROM tags WHERE guild_id = ? AND tag_name = ?""", (ctx.guild.id, tag_name.lower(), ))

        ress = await cur.fetchall()

        if not ress:
            await ctx.send(embed=discord.Embed(title='**Tag error**', description="> Error: Tag not found.", color=Color.red()))
            return
        res = ress[0]
        await ctx.send(f'{res[1]}')
        return

#    @fetch_tag.error
#    async def on_fetch_tag_error(self, ctx, error):
#        await ctx.send(embed=discord.Embed(title='**Fetchtag error**', description=f'> Error: {str(error)}', color=Color.red()))

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
