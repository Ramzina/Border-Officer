import discord
from discord import app_commands
from discord.ext import commands
from discord import Color
from datetime import datetime
import aiosqlite
import os
import asyncio
from discord.ui import Button,button, View
from random import randint

class CloseButton(View):
    def __init__(self):
        super().__init__(timeout=None)


    @button(label='Close ticket', style=discord.ButtonStyle.red,custom_id="closeticket", emoji="🔒")
    async def close(self, interaction:discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)

        view = CreateButton()
        view.message = await interaction.original_response()

        await view.message.edit(view=None)

        global ticket_creator
        ticket_creator = discord.utils.get(interaction.guild.members, id=int(interaction.channel.topic))
        await interaction.channel.set_permissions(ticket_creator, send_messages=False,read_message_history=False)

        await interaction.channel.send("Closing ticket...")
        await asyncio.sleep(2)

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel = False),
            ticket_creator: discord.PermissionOverwrite(read_messages=False, send_messages=False, view_channel=False),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }

        await interaction.channel.edit(overwrites=overwrites,name=f"Closed - {ticket_creator}", topic=f"Closed - {ticket_creator.id}")
        global msg
        msg = await interaction.channel.send(embed=discord.Embed(
            description=f'Ticket closed by {interaction.user.mention}. 🔒',
            color=Color.red()
        ),
        view=TrashOpenAndTranscriptButton())

class CreateButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label='Create Ticket', style=discord.ButtonStyle.blurple, emoji='🎫', custom_id='ticketopen')
    async def ticket(self, interaction:discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        global opener
        opener = interaction.user
        db = await aiosqlite.connect("ticketing.db")

        cur = await db.execute("""SELECT ticket_banned FROM ticketing WHERE guild_id = ?""", (interaction.guild.id, ))
        ticket_banned_role = await cur.fetchone()
        
        t_banned = discord.utils.get(interaction.guild.roles, id=ticket_banned_role[0])
        if t_banned in interaction.user.roles:
            await interaction.followup.send(embed=discord.Embed(
                description=f"{interaction.user.mention}, you are banned from making tickets.",
                color=Color.red()
            ),ephemeral=True)
            return

        cur = await db.execute("""SELECT ticket_category_id FROM ticketing WHERE guild_id = ?""", (interaction.guild.id, ))
        Category = await cur.fetchone()
        T_category = Category[0]

        category = discord.utils.get(interaction.guild.categories, id = T_category)
        for ch in category.text_channels:
            if ch.topic == f"{interaction.user.id}":
                await interaction.followup.send("You already have a ticket in {0}".format(ch.mention), ephemeral=True)
                return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel = True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await category.create_text_channel(
            name=f"{interaction.user}s ticket",
            topic=f'{interaction.user.id}',
            overwrites = overwrites
        )
        global meeswage
        meeswage = await channel.send(
            embed=discord.Embed(
            title=f"{interaction.user}'s Ban appeal ticket.",
            timestamp=datetime.utcnow(),
            description='Why you were banned (This will be checked),\nWhy you think you should be unbanned,\nWhat would you change to not be banned again.\n \nPlease don\'t spam support is being as fast as they can.',
            color=Color.green(),
            ),
        view=CloseButton())
        await interaction.followup.send(f'<#{channel.id}> created!', ephemeral=True)

class CreateCustomButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label='Create Ticket', style=discord.ButtonStyle.blurple, emoji='🎫', custom_id='ticketcustomopen')
    async def ticket(self, interaction:discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)
        global opener
        opener = interaction.user
        db = await aiosqlite.connect("ticketing.db")

        cur = await db.execute("""SELECT ticket_banned FROM customticketing WHERE guild_id = ?""", (interaction.guild.id, ))
        ticket_banned_role = await cur.fetchone()
        
        t_banned = discord.utils.get(interaction.guild.roles, id=ticket_banned_role[0])
        if t_banned in interaction.user.roles:
            await interaction.followup.send(embed=discord.Embed(
                description=f"{interaction.user.mention}, you are banned from making tickets.",
                color=Color.red()
            ),ephemeral=True)
            return

        cur = await db.execute("""SELECT ticket_category_id FROM customticketing WHERE guild_id = ?""", (interaction.guild.id, ))
        Category = await cur.fetchone()
        T_category = Category[0]

        category = discord.utils.get(interaction.guild.categories, id = T_category)
        for ch in category.text_channels:
            if ch.topic == f"{interaction.user.id}":
                await interaction.followup.send("You already have a ticket in {0}".format(ch.mention), ephemeral=True)
                return

        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, view_channel = True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        channel = await category.create_text_channel(
            name=f"{interaction.user}s ticket",
            topic=f'{interaction.user.id}',
            overwrites = overwrites
        )
        global meeswage
        meeswage = await channel.send(
            embed=discord.Embed(
            title=f"{interaction.user}'s support ticket.",
            timestamp=datetime.utcnow(),
            description='> Do not ping staff, they will be with you shortly.\n> Please tell us what you want us to know below.',
            color=Color.blurple(),
            ),
        view=CloseButton())
        await interaction.followup.send(f'<#{channel.id}> created!', ephemeral=True)

class TrashOpenAndTranscriptButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Open ticket", style=discord.ButtonStyle.green, emoji="🔓", custom_id="openticket")
    async def open(self, interaction:discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)

        await msg.edit(view=None)

        await interaction.edit_original_response(view=None)

        await interaction.channel.send("Opening ticket...")
        await asyncio.sleep(3)
        await interaction.followup.send(embed=discord.Embed(description=f"Ticket opened by {interaction.user.mention}. 🔓",color=Color.green()))

        ticket_creator = discord.utils.get(interaction.guild.members, id=int(interaction.channel.topic.replace('Closed - ', '')))


        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            ticket_creator: discord.PermissionOverwrite(read_messages=True,view_channel=True, send_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        await interaction.channel.edit(overwrites=overwrites,name=f'{ticket_creator}s ticket', topic=f'{ticket_creator.id}')

        await meeswage.edit(view=CloseButton())


    
    @button(label="Delete ticket", style=discord.ButtonStyle.red, emoji="⛔", custom_id="deleteticket")
    async def delete(self, interaction:discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)

        await msg.edit(view=None)

        await interaction.channel.send("Deleting ticket...")
        await asyncio.sleep(3)
        await interaction.followup.send(embed=discord.Embed(description=f"Ticket delted by {interaction.user.mention}. ⛔",color=Color.red()))
        await asyncio.sleep(1)

        db = await aiosqlite.connect("ticketing.db")
        try:
            cur = await db.execute("""SELECT auto_transcript FROM ticketing WHERE guild_id = ?""", (interaction.guild.id, ))
        except:
            cur = await db.execute("""SELECT auto_transcript FROM customticketing WHERE guild_id = ?""", (interaction.guild.id, ))

        auto_transcript = await cur.fetchone()
        if auto_transcript[0] == 'True':
            message_list = []
            async for message in interaction.channel.history(limit=None):
                message_list.append(message)

            with open(f"{interaction.channel.id}_{interaction.user}.txt", "a" ,encoding="utf=8") as f:
                        for message in reversed(message_list):
                            if message.embeds:
                                if message.embeds[0].title:
                                    f.write(f"TITLE - {message.embeds[0].title}\n")
                                if message.embeds[0].description:
                                    f.write(f"DESCRIPTION - {message.embeds[0].description}\n")
                                if len(message.embeds[0].fields) > 0:
                                    for field in message.embeds[0].fields:
                                        f.write(f"FIELD - {field.name} - {field.value}\n")
                                if message.embeds[0].footer:
                                    f.write(f"FOOTER - {message.embeds[0].footer.text}\n")
                                if message.embeds[0].image:
                                    f.write(f"IMAGE - {message.embeds[0].image.url}\n")
                                if message.embeds[0].thumbnail:
                                    f.write(f"THUMBNAIL - {message.embeds[0].thumbnail.url}\n")
                                if message.embeds[0].author:
                                    f.write(f"AUTHOR - {message.embeds[0].author.name}\n")
                                if message.embeds[0].url:
                                    f.write(f"LINK - {message.embeds[0].url}\n")
                                    f.write(f"LINK - {message.jump_url}\n\n")
                                continue
                            f.write(f"{message.author}: {message.content}\n")

            db = await aiosqlite.connect("config.db")
            cur = await db.execute("""SELECT channel_id FROM logs WHERE guild_id = ?""", (interaction.guild.id, ))

            channel = await cur.fetchone()
            chan = discord.utils.get(interaction.guild.text_channels, id=channel[0])
            if channel is None:
                await interaction.channel.send(f'Error sending transcript, run /logs and choose you bot logs channel.')
                await asyncio.sleep(3)
            if channel is not None:
                await chan.send(file=discord.File(f"{interaction.channel.id}_{interaction.user}.txt"))
                os.remove(f"{interaction.channel.id}_{interaction.user}.txt")

        await interaction.channel.delete()

    @button(label='Send transcript', style=discord.ButtonStyle.blurple, emoji="📑", custom_id='transcriptticket')
    async def transcript(self, interaction:discord.Interaction, button: Button):
        await interaction.response.defer(ephemeral=True)

        await interaction.followup.send('Sending transcript...')

        db = await aiosqlite.connect("config.db")
        cur = await db.execute("""SELECT * FROM logs WHERE guild_id=?""", (interaction.guild.id, ))

        row = await cur.fetchone()
        if row is None:
            await interaction.channel.send(f"To setup {self.bot.user}\'s commands properly, run /help and choose the BotSetup section")
            return
        cur = await db.execute("""SELECT channel_id FROM logs WHERE guild_id=?""", (interaction.guild.id, ))

        logs = await cur.fetchone()

        chan = discord.utils.get(interaction.guild.text_channels, id=logs[0])

        message_list = []
        async for message in interaction.channel.history(limit=None):
            message_list.append(message)

        with open(f"{interaction.channel.id}_{interaction.user}.txt", "a" ,encoding="utf=8") as f:
            for message in reversed(message_list):
                if message.embeds:
                    if message.embeds[0].title:
                        f.write(f"TITLE - {message.embeds[0].title}\n")
                    if message.embeds[0].description:
                        f.write(f"DESCRIPTION - {message.embeds[0].description}\n")
                    if len(message.embeds[0].fields) > 0:
                        for field in message.embeds[0].fields:
                            f.write(f"FIELD - {field.name} - {field.value}\n")
                    if message.embeds[0].footer:
                        f.write(f"FOOTER - {message.embeds[0].footer.text}\n")
                    if message.embeds[0].image:
                        f.write(f"IMAGE - {message.embeds[0].image.url}\n")
                    if message.embeds[0].thumbnail:
                        f.write(f"THUMBNAIL - {message.embeds[0].thumbnail.url}\n")
                    if message.embeds[0].author:
                        f.write(f"AUTHOR - {message.embeds[0].author.name}\n")
                    if message.embeds[0].url:
                        f.write(f"LINK - {message.embeds[0].url}\n")
                    f.write(f"LINK - {message.jump_url}\n\n")
                    continue
                f.write(f"{message.author}: {message.content}\n")
        await chan.send(file=discord.File(f"{interaction.channel.id}_{interaction.user}.txt"))
        os.remove(f"{interaction.channel.id}_{interaction.user}.txt")

        await interaction.followup.send(embed=discord.Embed(description=f"Transcript sent to <#{chan.id}> by {interaction.user.mention}. 📑",color=Color.blurple()))





class Ticketing(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    

    @app_commands.command(name='appeal-ticket', description='Sets the ticket channel.')
    @app_commands.describe(channel='The channel the open ticket button will be in', ticket_category='The category opened tickets will be in', ticket_banned='A role that bans users from creating tickets.', auto_transcript='Automatically sends the ticket transcript to the logs channel.')
    @app_commands.default_permissions(administrator=True)
    async def createticket(self, interaction:discord.Interaction, channel:discord.TextChannel,ticket_category:discord.CategoryChannel,ticket_banned:discord.Role, auto_transcript:bool=False):
        await interaction.response.defer(ephemeral=True,thinking=True)
        db = await aiosqlite.connect("ticketing.db")
        await db.execute("""CREATE TABLE IF NOT EXISTS ticketing(guild_name STRING, guild_id INTEGER, ticket_category_id INTEGER, ticket_channel_id INTEGER,ticket_banned INTEGER,auto_transcript STRING)""")
        cur = await db.execute("""SELECT * FROM ticketing WHERE guild_id = ?""", (interaction.guild.id, ))
        row = await cur.fetchone()
        if row is None:
            await db.execute("""INSERT INTO ticketing(guild_name, guild_id, ticket_category_id, ticket_channel_id,ticket_banned ,auto_transcript) VALUES (?,?,?,?,?,?)""", (interaction.guild.name, interaction.guild.id, ticket_category.id, channel.id,ticket_banned.id, str(auto_transcript), ))
            await db.commit()
            await interaction.followup.send(f'{interaction.user.mention}, set "{ticket_category}" as ticket category <#{channel.id}> as the ticket channel and <@&{ticket_banned.id}> as the banned role!')
            await channel.send(embed=discord.Embed(
                title='**Blacklist Appeals**',
                description='Click the button below to make a blacklist appeal.',color=Color.green(), 
            ),view=CreateButton())
        else:
            await db.execute("""UPDATE ticketing SET ticket_category_id = ?, ticket_channel_id = ?,ticket_banned=? ,auto_transcript = ? WHERE guild_id = ?""", (ticket_category.id,channel.id,ticket_banned.id,str(auto_transcript), interaction.guild.id, ))
            await db.commit()
            await interaction.followup.send(f'{interaction.user.id}, set "{ticket_category}" as ticket category, <#{channel.id}> as the ticket channel and <@&{ticket_banned.id}> as the banned role!')
            await channel.send(embed=discord.Embed(
                title='**Blacklist Appeals**',
                description='Click the button below to make a blacklist appeal.',color=Color.green()
            ),view=CreateButton())


    @app_commands.command(name='create-ticket', description='Creates a clickable ticket in the channel command is run in.')
    @app_commands.default_permissions(administrator=True)
    async def createcustomticket(self, interaction:discord.Interaction,ticket_title:str, ticket_info:str, channel:discord.TextChannel,ticket_category:discord.CategoryChannel,ticket_banned:discord.Role, auto_transcript:bool=False):
        await interaction.response.defer(ephemeral=True,thinking=True)
        db = await aiosqlite.connect("ticketing.db")
        await db.execute("""CREATE TABLE IF NOT EXISTS customticketing(guild_name STRING, guild_id INTEGER, ticket_category_id INTEGER, ticket_channel_id INTEGER,ticket_banned INTEGER,auto_transcript STRING)""")
        cur = await db.execute("""SELECT * FROM customticketing WHERE guild_id = ?""", (interaction.guild.id, ))
        row = await cur.fetchone()
        if row is None:
            await db.execute("""INSERT INTO customticketing(guild_name, guild_id, ticket_category_id, ticket_channel_id,ticket_banned ,auto_transcript) VALUES (?,?,?,?,?,?)""", (interaction.guild.name, interaction.guild.id, ticket_category.id, channel.id,ticket_banned.id, str(auto_transcript), ))
            await db.commit()
            await interaction.followup.send(f'{interaction.user.mention}, set "{ticket_category}" as ticket category <#{channel.id}> as the ticket channel and <@&{ticket_banned.id}> as the banned role!')
            await channel.send(embed=discord.Embed(
                title=f'**{ticket_title.capitalize()}**',
                description=ticket_info.capitalize(),color=Color.green(), 
            ), view=CreateCustomButton())
        else:
            await db.execute("""UPDATE customticketing SET ticket_category_id = ?, ticket_channel_id = ?,ticket_banned=? ,auto_transcript = ? WHERE guild_id = ?""", (ticket_category.id,channel.id,ticket_banned.id,str(auto_transcript), interaction.guild.id, ))
            await db.commit()
            await interaction.followup.send(f'{interaction.user.mention}, set "{ticket_category}" as ticket category, <#{channel.id}> as the ticket channel and <@&{ticket_banned.id}> as the banned role!')
            await channel.send(embed=discord.Embed(
                title=f'**{ticket_title.capitalize()}**',
                description=ticket_info.capitalize(),color=Color.green(), 
            ), view=CreateCustomButton())


async def setup(bot):
    await bot.add_cog(Ticketing(bot))
