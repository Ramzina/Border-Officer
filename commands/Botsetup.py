import discord
import aiosqlite
from discord import Color
from discord import ui
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from discord.app_commands import AppCommandError
from typing import Optional

from discord.interactions import Interaction

class JoinDmMessages(ui.Modal, title='Join dm messages.'):
	joinMessageContent = ui.TextInput(label='What should be sent to joining members?',placeholder=f'**Welcome to "Guild Name"\n \n*Make sure to read the rules and have a fun time!*' ,style=discord.TextStyle.paragraph)
	
	async def on_submit(self, interaction: discord.Interaction):
		await interaction.response.defer(ephemeral=True, thinking=True)

		db = await aiosqlite.connect("config.db")

		await db.execute("""CREATE TABLE IF NOT EXISTS dmmessages(guild_name TEXT, guild_id INTEGER, join_message TEXT)""")

		cur = await db.execute("""SELECT join_message FROM dmmessages WHERE guild_id = ?""", (interaction.guild.id, ))
		res = await cur.fetchone()

		if res is None:
			await db.execute("""INSERT INTO dmmessages(guild_name, guild_id, join_message) VALUES (?,?,?)""", (interaction.guild.name, interaction.guild.id, self.joinMessageContent.value, ))
			await db.commit()
		else:
			await db.execute("""UPDATE dmmessages SET join_message = ? WHERE guild_id = ?""", (self.joinMessageContent.value, interaction.guild.id, ))
			await db.commit()
		await interaction.followup.send(f'The following message will be sent to joining members:\n{self.joinMessageContent}')


class Setup(commands.Cog):
	def __init__(self, bot):
		self.bot = bot	

	@app_commands.command(name='setup-count', description='Sets up the counting feature on the bot.')
	@app_commands.default_permissions(administrator=True)
	async def count_setup(self, interaction:discord.Interaction, counting_channel:discord.TextChannel):
		await interaction.response.defer(ephemeral=True, thinking=True)

		db = await aiosqlite.connect("counting.db")
		await db.execute("""CREATE TABLE IF NOT EXISTS counting(guild_name TEXT, guild_id INTEGER,count_channel INTEGER, number INTEGER, last_user INTEGER)""")
		await db.execute("""CREATE TABLE IF NOT EXISTS saves(guild_name TEXT, guild_id INTEGER,user INTEGER, saves INTEGER)""")


		cur = await db.execute("""SELECT number FROM counting WHERE guild_id = ?""", (interaction.guild.id, ))
		res = await cur.fetchone()

		if res is None:
			await db.execute("""INSERT INTO counting(guild_name,count_channel ,guild_id, number) VALUES (?,?,?,?)""", (interaction.guild.name, counting_channel.id,interaction.guild.id, 1, ))
			await db.commit()
            
			cout = int(1)

			await interaction.followup.send(embed=discord.Embed(title='**Setup count**', description=f'> Setup count successfully', color=Color.green()), ephemeral=True)
			await counting_channel.send(embed=discord.Embed(title='**Count channel set**', description=f'> Counting channel set successfully!\n> Next number: {cout}', color=Color.blurple()))
		else:
			await db.execute("""UPDATE counting SET count_channel = ? WHERE guild_id = ?""", (counting_channel.id,interaction.guild.id, ))
			await db.commit()

			cout = int(res[0])

			await interaction.followup.send(embed=discord.Embed(title='**Setup count**', description=f'> Setup count successfully\n> Count: {cout}', color=Color.green()), ephemeral=True)
			await counting_channel.send(embed=discord.Embed(title='**Count channel set**', description=f'> Counting channel set successfully!\n> Next number: {cout}', color=Color.blurple()))

	@app_commands.command(name='setup-lockdown', description='Sets up the lockdown command.')
	@app_commands.default_permissions(manage_channels=True)
	@app_commands.describe(role='The role that gets affected when using /lockdown')
	async def setuplockdown(self, interaction:discord.Interaction, role:discord.Role):
		await interaction.response.defer(ephemeral=True)

		db= await aiosqlite.connect("config.db")

		await db.execute("""CREATE TABLE IF NOT EXISTS lockdown(guild_name STRING, guild_id INTEGER, locked_role INTEGER)""")

		cur = await db.execute("""SELECT locked_role FROM blacklisted WHERE guild_id = ?""", (interaction.guild.id, ))

		res = await cur.fetchone()

		if res is None:
			await db.execute("""INSERT INTO blacklisted(guild_name, guild_id, locked_role) VALUES (?,?,?)""", (interaction.guild.name, interaction.guild.id, role.id, ))
			await db.commit()

			await interaction.followup.send(embed=
											discord.Embed(
				
												title='**Lockdown role set**',
												description=f'> Lockdown role: <&@{role.id}>\n> Set by: {interaction.user.mention}',color=Color.green(),
											))
			

		else:
			await db.execute("""UPDATE blacklisted SET locked_role = ? WHERE guild_id = ?""", (role.id, interaction.guild.id, ))
			await db.commit()

			await interaction.followup.send(embed=
											discord.Embed(
				
												title='**Lockdown role set**',
												description=f'> Lockdown role: <&@{role.id}>\n> Set by: {interaction.user.mention}',color=Color.green(),
											))
			


	@app_commands.command(name='logs', description='Sets the logs channel.')
	@app_commands.default_permissions(administrator=True)
	async def logs(self, interaction:discord.Interaction, channel:discord.TextChannel):
			print('[Logs] has just been executed!')
			await interaction.response.defer(ephemeral=True, thinking=True)

			db = await aiosqlite.connect("config.db")
			await db.execute("CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)")
		
			cur = await db.execute("SELECT * FROM logs WHERE guild_id = ?", (interaction.guild.id, ))		
			row = await cur.fetchone()
			if row is None:

					await db.execute("""INSERT INTO logs VALUES(?, ?, ?)""",(interaction.guild.name, interaction.guild.id, channel.id, ))
					await db.commit()
		
					await interaction.followup.send(f'{interaction.user.mention}, <#{channel.id}> has been set as the logs channel for this guild.')
					channel = self.bot.get_channel(channel.id)

					embed=discord.Embed(title='! **LOGS** !', description=f'{interaction.user.mention} has set this channel as the logs channel!',timestamp=datetime.utcnow(), color=Color.from_rgb(27, 152, 250))
					await channel.send(embed=embed.set_thumbnail(url=interaction.user.avatar.url))

			else:
					
					await cur.execute("""UPDATE logs SET channel_id = ? WHERE guild_id = ?""", (channel.id, interaction.guild.id, ))
					await db.commit()

					await interaction.followup.send(f'{interaction.user.mention}, <#{channel.id}> has been set as the logs channel for this guild.')
					channel = self.bot.get_channel(channel.id)

					embed=discord.Embed(title='! **LOGS** !', description=f'{interaction.user.mention} has set this channel as the logs channel!',timestamp=datetime.utcnow(), color=Color.from_rgb(27, 152, 250))
					await channel.send(embed=embed.set_thumbnail(url=interaction.user.avatar.url))


	@app_commands.command(name="setupblacklist", description="Sets up the /blacklist command.")
	@app_commands.default_permissions(administrator=True)
	async def setupblacklist(self, interaction:discord.Interaction, banned_role:discord.Role, appeal_channel:discord.TextChannel, jail_chat: Optional[discord.TextChannel] = None):
		print('[Setupblacklist] has just been executed!')
		await interaction.response.defer(ephemeral=True, thinking=True)

		db = await aiosqlite.connect("config.db")

		await db.execute("CREATE TABLE IF NOT EXISTS blacklist(guild_name STRING, guild_id INTEGER, banned_role_id INTEGER, appeals_id INTEGER, jail_id INTEGER)")
		
		cur = await db.execute("SELECT * FROM blacklist WHERE guild_id = ?", (interaction.guild.id, ))
		row = await cur.fetchone()
		if row is None:
			if jail_chat is None:
				await cur.execute("""INSERT INTO blacklist VALUES(?,?,?,?,?)""", (interaction.guild.name, interaction.guild.id, banned_role.id, appeal_channel.id, None, ))
				await db.commit()
				
			if jail_chat is not None:
				await cur.execute("""INSERT INTO blacklist VALUES(?,?,?,?,?)""", (interaction.guild.name, interaction.guild.id, banned_role.id, appeal_channel.id, jail_chat.id, ))  
				await db.commit()

			for channel in interaction.guild.channels:

				if channel.id == appeal_channel:
					await channel.set_permissions(banned_role, view_channel=True, send_messages=False)
					await channel.set_permissions(interaction.guild.default_role, view_channel=False)
				elif channel.id == jail_chat:
					await channel.set_permissions(banned_role, view_channel=True, send_messages =True)
					await channel.set_permissions(interaction.guild.default_role, view_channel=False)
				else: 
					await channel.set_permissions(banned_role, view_channel=False, send_messages=False)


			await interaction.followup.send(f'{interaction.user.mention}, "<@&{banned_role.id}>" is now the banned role and <#{appeal_channel.id}> is now the appeals channel for this guild.')
			if jail_chat is not None:
				await jail_chat.send(
					embed=discord.Embed(
					title="**Jail**",
					description=f"> This channel was set as the jail channel.",
					color=Color.green()
					)
				)

		else:
			await cur.execute("""UPDATE blacklist SET banned_role_id = ?, appeals_id = ? WHERE guild_id = ?""", (banned_role.id, appeal_channel.id, interaction.guild.id))
			await db.commit()
			await interaction.followup.send(f'{interaction.user.mention}, "<@&{banned_role.id}>" is now the banned role and <#{appeal_channel.id}> is now the appeals channel for this guild.')

			for channel in interaction.guild.channels:

				if channel.id == appeal_channel:
					await channel.set_permissions(banned_role, view_channel=True, send_messages=False)
					await channel.set_permissions(interaction.guild.default_role, view_channel=False)
				elif channel.id == jail_chat:
					await channel.set_permissions(banned_role, view_channel=True, send_messages =True)
					await channel.set_permissions(interaction.guild.default_role, view_channel=False)
				else: 
					await channel.set_permissions(banned_role, view_channel=False, send_messages=False)

			if jail_chat is not None:		
				await jail_chat.send(
					embed=discord.Embed(
					title="**Jail**",
					description=f"> This channel was set as the jail channel.",
					color=Color.green()
					)
				)
	
	@app_commands.command(name='welcome-messages', description='Toggles welcome messages.')
	@app_commands.default_permissions(administrator=True)
	async def togglewelcome(self, interaction:discord.Interaction, toggle:bool):
		print('[Togglewelcome] has just been executed!')
		await interaction.response.defer(ephemeral=True, thinking=True)

		db = await aiosqlite.connect("config.db")
		  
		await db.execute("""CREATE TABLE IF NOT EXISTS welcome(guild_name STRING, guild_id INTEGER, channel_id INTEGER, toggle STRING)""")

		cur = await db.execute("""SELECT * FROM welcome WHERE guild_id = ?""", (interaction.guild.id, ))
		row = cur.fetchone()
		if row is None:

			await db.execute("""
							INSERT INTO welcome VALUES
							guild_name = ?
							guild_id = ?
							toggle = ?
							WHERE guild_id = ?
							""", (interaction.guild.name, interaction.guild.id, str(toggle), ))
		else:
			await db.execute("""UPDATE welcome
							SET toggle = ? WHERE guild_id = ?""", (str(toggle), interaction.guild.id))
		await db.commit()
		await interaction.followup.send(f'{interaction.user.mention}, welcome messages have been set to {toggle}')



	@app_commands.command(name='joinroles', description='Sets the role given to joining members.')
	@app_commands.default_permissions(administrator=True)
	async def joinroles(self, interaction:discord.Interaction, role:discord.Role):
		print('[Joinroles] has just been executed!')
		await interaction.response.defer(ephemeral=True, thinking=True)

		db = await aiosqlite.connect("config.db")

		await db.execute("""CREATE TABLE IF NOT EXISTS joinroles(guild_name STRING, guild_id, role_id, toggle STRING)""")

		res = await db.execute("""SELECT role_id FROM joinroles WHERE guild_id = ?""", (interaction.guild.id, ))
		row = await res.fetchone()
		if row is None:
			await db.execute("""INSERT INTO joinroles (guild_name, guild_id, role_id, toggle) VALUES(?,?,?,?)""", (interaction.guild.name, interaction.guild.id, role.id, 'True'))
			await db.commit()
			await interaction.followup.send(f'{interaction.user.mention}, <@&{role.id}> has been set as the join role and join roles have been toggled to True.')
		else:
			await db.execute("""UPDATE joinroles set role_id = ?""", (role.id, ))
			await db.commit()
			await interaction.followup.send(f'{interaction.user.mention}, <@&{role.id}> has been set as the join role.')

	
	@app_commands.command(name='togglejoinroles', description='Toggles join roles.')
	@app_commands.default_permissions(administrator=True)
	async def togglejoinroles(self, interaction:discord.Interaction, toggle:bool):
		print('[Togglejoinroles] has just been executed!')
		await interaction.response.defer(ephemeral=True, thinking=True)

		db = await aiosqlite.connect("config.db")
		  
		await db.execute("""CREATE TABLE IF NOT EXISTS joinroles(guild_name STRING, guild_id INTEGER, channel_id INTEGER, toggle STRING)""")

		cur = await db.execute("""SELECT * FROM joinroles WHERE guild_id = ?""", (interaction.guild.id, ))
		row = await cur.fetchone()
		if row is None:
			await interaction.followup.send(f'{interaction.user.mention}, to run this command you need to run /joinroles.')
			return

		await db.execute("""
							UPDATE joinroles
							SET toggle = ?
							WHERE guild_id = ?
							""", (str(toggle), interaction.guild.id, ))
		await db.commit()
		await interaction.followup.send(f'{interaction.user.mention}, join roles have been set to {toggle}')

	@app_commands.command(name='dm-join-messages', description='Sends message to joining members.')
	@app_commands.default_permissions(administrator=True)
	async def dmjoinmessages(self, interaction:discord.Interaction):
		await interaction.response.send_modal(JoinDmMessages())


async def setup(bot):
	await bot.add_cog(Setup(bot))
