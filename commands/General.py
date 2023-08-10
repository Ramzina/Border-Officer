from discord import Color
import discord
from discord import ui
from discord.interactions import Interaction
import python_weather
import random
from discord.ext.commands import (
	CommandNotFound,
	CommandOnCooldown,
	MissingPermissions,
	MissingRequiredArgument,
)
from datetime import datetime
from discord.app_commands import AppCommandError
import aiosqlite
from discord.ext import commands, tasks
from discord import app_commands
import random


class General(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

		

####################################################################################################################################
#################################################################################################################################### ECHO START
####################################################################################################################################

	@app_commands.command(name="echo", description="The bot says what you pass. (Backtraceable)")
	@app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
	async def echo(self, interaction: discord.Interaction, message: str) -> None:
		print("[Echo] has just been executed")
		await interaction.response.defer(thinking=True)

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

		channel = self.bot.get_channel(logs)
		await interaction.followup.send(f"{message}")
		embed = discord.Embed(
			title="! **ECHO** !", description=f"- 🧍 User: {interaction.user.mention}\n- 🪪 User name: {interaction.user}\n- 🪪 User Id: `{interaction.user.id}`\n- 🖊️ Message: {message}",timestamp=datetime.utcnow(),color=Color.from_rgb(27, 152, 250)
		)
		if logs is not None: await channel.send(embed=embed.set_thumbnail(url=interaction.user.avatar.url))
	@echo.error
	async def on_echo_error(
		self, interaction: discord.Interaction, error: AppCommandError
	):
		if isinstance(error, app_commands.CommandOnCooldown):
			await interaction.response.send_message(content=str(error), ephemeral=True)

####################################################################################################################################
#################################################################################################################################### ECHO END, KYS START
####################################################################################################################################

	@app_commands.command(
		name="kys", description="Tells the specified user to kill themself"
	)
	@app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
	async def kys(
		self, interaction: discord.Interaction, member: discord.Member
	) -> None:
		print("[Kys] has just been executed")
		await interaction.response.defer(thinking=True)

		if member.id == interaction.user.id:
			await interaction.followup.send(embed=discord.Embed(title="**Kys error**",description=f'> Error: `Member is same as executing user`', color=Color.red()))
			return
		embed = discord.Embed(
			title="**Kys**",
			description=f"\n> Alert: {member.mention}, {interaction.user.mention} thinks you should carve your wrists!:O",
			timestamp=datetime.utcnow(),
			color=Color.green())
		await interaction.followup.send(embed=embed)
	@kys.error
	async def on_kys_error(
		self, interaction: discord.Interaction, error: AppCommandError
	):
		if isinstance(error, app_commands.CommandOnCooldown):
			await interaction.response.send_message(content=str(error), ephemeral=True)


####################################################################################################################################
#################################################################################################################################### KYS END, PING START
####################################################################################################################################

	@app_commands.command(name="ping", description="Sends the bots latency in a cool embed!")
	@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id, i.user.id))
	async def ping(self, interaction: discord.Interaction):
		print("[Ping] has just been executed")
		await interaction.response.defer(ephemeral=True)

		if round(self.bot.latency * 1000) < 150:
			COLOR=Color.green()
			result = 'Fast'
		elif round(self.bot.latency * 1000) < 200:
			COLOR=Color.yellow()
			result = 'Average'
		elif round(self.bot.latency * 1000) > 300:
			COLOR=Color.red()
			result = 'Slow'

		embed = discord.Embed(
			title="**Ping**",
			description=f"> Latency: {round(self.bot.latency * 1000)}ms 🏓\n> Speed: {result}",
			color=COLOR,
		)

		await interaction.followup.send(
			embed=embed, ephemeral=True
		)

	@ping.error
	async def on_ping_error(
		self, interaction: discord.Interaction, error: AppCommandError
	):
		if isinstance(error, app_commands.CommandOnCooldown):
			await interaction.response.send_message(content=str(error), ephemeral=True)

####################################################################################################################################
#################################################################################################################################### PING END,  START
####################################################################################################################################

	@app_commands.command(
		name="random", description="Gives a random number between the two you pass."
	)
	@app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
	async def random(
		self, interaction: discord.Interaction, num1: int = 1, num2: int = 100):

		print("[Random] has just been executed")

		await interaction.response.send_message(embed=discord.Embed(title="**Random**",description=f"> Number: {random.randint(num1, num2)}",color=Color.green()))

	@random.error
	async def on_random_error(
		self, interaction: discord.Interaction, error: AppCommandError
	):
		if isinstance(error, app_commands.CommandOnCooldown):
			await interaction.response.send_message(content=str(error), ephemeral=True)

####################################################################################################################################
#################################################################################################################################### RANDOM END, WEATHER START
####################################################################################################################################

	@app_commands.command(name='weather', description='Gets the forecast in the selected city.')
	@app_commands.checks.cooldown(1,15, key=lambda i: (i.guild.id, i.user.id))
	async def weather(self, interaction:discord.Interaction, city:str, private:bool=False):
		await interaction.response.defer(ephemeral=private, thinking=True)
		print('[Weather] has just been executed.')
		async with python_weather.Client(unit=python_weather.METRIC) as client:
			weather = await client.get(city)
			embed = discord.Embed(title=f'**Weather in {city.capitalize()}**', description=f"> ☁️ Weather: {weather.current.description}\n> 🌥️ Temperature: {weather.current.temperature}C°\n> 💦 Humidity: {weather.current.humidity}%\n> 🚩 Wind speed: {weather.current.wind_speed} Km/h\n> 🚩 Wind direction: {weather.current.wind_direction}",
			color=Color.blue())
			await interaction.followup.send(embed= discord.Embed(title=f'**Weather in {city.capitalize()}**', description=f"> ☁️ Weather: {weather.current.description}\n> 🌥️ Temperature: {weather.current.temperature}C°\n> 💦 Humidity: {weather.current.humidity}%\n> 🚩 Wind speed: {weather.current.wind_speed} Km/h\n> 🚩 Wind direction: {weather.current.wind_direction}",color=Color.blue()))
	@weather.error
	async def on_weather_error(self, interaction: discord.Interaction, error: AppCommandError):
		if isinstance(error, app_commands.CommandOnCooldown): await interaction.response.send_message(embed=discord.Embed(title='**Weather error**', description=f'> Error: {str(error)}'), ephemeral=True)


####################################################################################################################################
#################################################################################################################################### WEATHER END, 8BALL START
####################################################################################################################################

	@app_commands.command(name='8ball', description='Ask the holy 8ball a question!')
	@app_commands.checks.cooldown(1,15, key=lambda i: (i.guild.id, i.user.id))
	async def eightball(self,interaction:discord.Interaction, question:str):
		await interaction.response.defer(ephemeral=True, thinking=True)
		print('[8ball] has just been executed.')

		possible_answers = ['Yes.', 'No.', 'Possibly.', 'Maybe.', 'The stars tell me yes.', 'The stars tell me no.', 'The stars are unsure.', 'The stars don\'t know yet.','Fuck it sure.', 'Why not.', 'Sure', 'No fuck off.', 'Lmao never.', 'Always.', 'I don\'t fucking know.', 'YEP', '10000%', 'I think so ¯\_(ツ)_/¯']

		answer = random.choice(possible_answers)


		await interaction.followup.send(embed=discord.Embed(title='**The magic 8ball**', description=f'- {interaction.user.mention} asked: "{question}"\n- Magic 8ball says: "{answer}"', color=Color.green()))

####################################################################################################################################
#################################################################################################################################### 8BALL END
####################################################################################################################################



async def setup(bot):
	await bot.add_cog(General(bot))
