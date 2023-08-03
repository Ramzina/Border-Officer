import discord
import aiosqlite
from discord import Color
from discord.ext import commands
from discord import app_commands
from datetime import datetime
from discord.app_commands import AppCommandError
from typing import Optional

class Setup(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@app_commands.command(name='welcome', description='Sets the welcome message channel.')
	@app_commands.default_permissions(administrator=True)
	async def welcome(self, interaction:discord.Interaction, channel:discord.TextChannel):
			print('[Welcome] has just been executed!')
			await interaction.response.defer(ephemeral=True, thinking=True)


			db = await aiosqlite.connect("config.db")
			await db.execute("CREATE TABLE IF NOT EXISTS welcome(guild_name STRING, guild_id INTEGER, channel_id INTEGER, toggle STRING)")
		
			cur = await db.execute("SELECT * FROM welcome WHERE guild_id = ?", (interaction.guild.id, ))
			row = await cur.fetchone()
			if row is None:

					await cur.execute("""
								INSERT INTO welcome VALUES
								(?, ?, ?, ?)
								""", (interaction.guild.name, interaction.guild.id, channel.id, 'True', ))
					
					await db.commit()
		
					await interaction.followup.send(f'{interaction.user.mention}, <#{channel.id}> has been set as the welcome channel for this guild.')

			else:
					await cur.execute("""
								UPDATE welcome
								SET channel_id = ?
								WHERE guild_id = ?
								""", (channel.id, interaction.guild.id, ))

					await db.commit()	
					await interaction.followup.send(f'{interaction.user.mention}, <#{channel.id}> has been set as the welcome channel for this guild.')			

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
				
			else:
				await cur.execute("""INSERT INTO blacklist VALUES(?,?,?,?,?)""", (interaction.guild.name, interaction.guild.id, banned_role.id, appeal_channel.id, jail_chat.id, ))  
				await db.commit()

			for channel in interaction.guild.channels:
				if channel != appeal_channel or channel != jail_chat: 
					await channel.set_permissions(banned_role, view_channel=False)

				else:
					for role in interaction.guild.roles:
						if role != banned_role:
							await channel.set_permissions(role, view_channel=False)
					await channel.set_permissions(banned_role, view_channel=True)

			await interaction.followup.send(f'{interaction.user.mention}, "<@&{banned_role.id}>" is now the banned role and <#{appeal_channel.id}> is now the appeals channel for this guild.')
			if jail_chat is not None:
				await jail_chat.send(
					embed=discord.Embed(
					title="! **JAIL** !",
					description=f"{interaction.user.mention}, has set this channel as the jail channel!",
					timestamp=datetime.utcnow(),
					color=Color.from_rgb(27, 152, 250)
					).set_thumbnail(url=interaction.user.avatar.url)
				)

		else:
			await cur.execute("""UPDATE blacklist SET banned_role_id = ?, appeals_id = ? WHERE guild_id = ?""", (banned_role.id, appeal_channel.id, interaction.guild.id))
			await db.commit()
			await interaction.followup.send(f'{interaction.user.mention}, "<@&{banned_role.id}>" is now the banned role and <#{appeal_channel.id}> is now the appeals channel for this guild.')

			for channel in interaction.guild.channels:

				if channel == appeal_channel or channel == jail_chat:
					await channel.set_permissions(banned_role, view_channel=True)
					await channel.set_permissions(interaction.guild.default_role, view_channel=False)
				else: 
					await channel.set_permissions(banned_role, view_channel=False)

			if jail_chat is not None:		
				await jail_chat.send(
					embed=discord.Embed(
					title="! **JAIL** !",
					description=f"{interaction.user.mention}, has set this channel as the jail channel!",
					timestamp=datetime.utcnow(),
					color=Color.from_rgb(27, 152, 250)
					).set_thumbnail(url=interaction.user.avatar.url)
				)
	
	@app_commands.command(name='togglewelcome', description='Toggles welcome messages.')
	@app_commands.default_permissions(administrator=True)
	async def togglewelcome(self, interaction:discord.Interaction, toggle:bool):
		print('[Togglewelcome] has just been executed!')
		await interaction.response.defer(ephemeral=True, thinking=True)

		db = await aiosqlite.connect("config.db")
		  
		await db.execute("""CREATE TABLE IF NOT EXISTS welcome(guild_name STRING, guild_id INTEGER, channel_id INTEGER, toggle STRING)""")

		cur = await db.execute("""SELECT * FROM welcome WHERE guild_id = ?""", (interaction.guild.id, ))
		row = cur.fetchone()
		if row is None:
			await interaction.followup.send(f'{interaction.user.mention}, to run this command you need to run /welcome.')
			return

		await db.execute("""
							UPDATE welcome
							SET toggle = ?
							WHERE guild_id = ?
							""", (str(toggle), interaction.guild.id, ))
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



async def setup(bot):
	await bot.add_cog(Setup(bot))
