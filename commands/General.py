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

	@commands.hybrid_command(name="echo", description="The bot says what you want it to.")
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def echo(self, ctx, * ,message: str) -> None:
		print("[Echo] has just been executed")
		await ctx.defer()

		db = await aiosqlite.connect("config.db")

		await db.execute(
			"""CREATE TABLE IF NOT EXISTS logs(guild_name STRING, guild_id INTEGER, channel_id INTEGER)"""
		)
		res = await db.execute(
			f"""SELECT * FROM logs WHERE guild_id = {ctx.guild.id}"""
		)
		row = await res.fetchone()
		if row is None:
			await ctx.followup.send(f'{ctx.user.mention}, To setup {self.bot.user}\'s commands properly, run /logs to set a commands log channel')

		res = await db.execute(
			f"""SELECT channel_id FROM logs WHERE guild_id = {ctx.guild.id}"""
		)
		channel = await res.fetchone()
		logs = channel[0]

		channel = self.bot.get_channel(logs)
		await ctx.send(f"{message}")
		embed = discord.Embed(
			title="! **ECHO** !", description=f"- 🧍 User: {ctx.author.mention}\n- 🪪 User name: {ctx.author}\n- 🪪 User Id: `{ctx.author.id}`\n- 🖊️ Message: {message}",timestamp=datetime.utcnow(),color=Color.from_rgb(27, 152, 250)
		)
		if logs is not None: await channel.send(embed=embed.set_thumbnail(url=ctx.author.avatar.url))
	@echo.error
	async def on_echo_error(
		self, ctx, error: CommandOnCooldown
	):
		await ctx.send(embed=discord.Embed(title='*Echo error**', description=f'> Error: {str(error)}', color=Color.red()))

####################################################################################################################################
#################################################################################################################################### ECHO END, KYS START
####################################################################################################################################

	@commands.hybrid_command(
		name="kys", description="Tells the specified user to kill themself"
	)
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def kys(
		self, ctx, member: discord.Member
	) -> None:
		print("[Kys] has just been executed")
		await ctx.defer()

		if member.id == ctx.author.id:
			await ctx.send(embed=discord.Embed(title="**Kys error**",description=f'> Error: `Member is same as executing user`', color=Color.red()), ephemeral = True)
			return
		embed = discord.Embed(
			title="**Kys**",
			description=f"\n> Alert: {member.mention}, {ctx.author.mention} thinks you should carve your wrists!:O",
			color=Color.green())
		await ctx.send(embed=embed)
	@kys.error
	async def on_kys_error(
		self, ctx, error: CommandOnCooldown
	):
		await ctx.send(embed=discord.Embed(title='**Kys error**', description=f'> Error: {str(error)}', color=Color.red()))


####################################################################################################################################
#################################################################################################################################### KYS END, PING START
####################################################################################################################################

	@commands.hybrid_command(name="ping", description="Sends the bots latency in a cool embed!")
	@commands.cooldown(1, 5, commands.BucketType.user)
	async def ping(self, ctx):
		print("[Ping] has just been executed")
		await ctx.defer()

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

		await ctx.send(embed=embed, ephemeral=True)

	@ping.error
	async def on_ping_error(
		self, ctx, error: CommandOnCooldown
	):
		await ctx.send(embed=discord.Embed(title='**Ping error**', description=f'> Error: {str(error)}', color=Color.red()))

####################################################################################################################################
#################################################################################################################################### PING END,  START
####################################################################################################################################

	@commands.hybrid_command(
		name="random", description="Gives a random number between the two you pass."
	)
	@commands.cooldown(1, 10, commands.BucketType.user)
	async def random(
		self, ctx, num1: int = 1, num2: int = 100):
		print("[Random] has just been executed")
		await ctx.defer()

		await ctx.send(embed=discord.Embed(title="**Random**",description=f"> Number: {random.randint(num1, num2)}",color=Color.green()))

	@random.error
	async def on_random_error(
		self, ctx, error: CommandOnCooldown
	):
		await ctx.send(embed=discord.Embed(title='**Random error**', description=f'> Error: {str(error)}', color=Color.red()))
####################################################################################################################################
#################################################################################################################################### RANDOM END, WEATHER START
####################################################################################################################################

	@commands.hybrid_command(name='weather', description='Gets the forecast in the selected city.')
	@commands.cooldown(1,15, commands.BucketType.user)
	async def weather(self, ctx, *, city:str):
		print('[Weather] has just been executed.')
		await ctx.defer()

		msg = await ctx.send(embed=discord.Embed(description='🌥️ Fetching weather...', color=Color.yellow()))

		async with python_weather.Client(unit=python_weather.METRIC) as client:
			weather = await client.get(city)
			await msg.edit(discord.Embed(title=f'**Weather in {city.capitalize()}**', description=f"> ☁️ Weather: {weather.current.description}\n> 🌥️ Temperature: {weather.current.temperature}C°\n> 💦 Humidity: {weather.current.humidity}%\n> 🚩 Wind speed: {weather.current.wind_speed} Km/h\n> 🚩 Wind direction: {weather.current.wind_direction}",
			color=Color.blue()))
	@weather.error
	async def on_weather_error(self, ctx, error: CommandOnCooldown):
		await ctx.send(embed=discord.Embed(title='**Weather error**', description=f'> Error: {str(error)}', color=Color.red()))

####################################################################################################################################
#################################################################################################################################### WEATHER END, 8BALL START
####################################################################################################################################

	@commands.hybrid_command(name='8ball', description='Ask the holy 8ball a question!')
	@commands.cooldown(1,15, commands.BucketType.user)
	async def eightball(self,ctx,* ,question:str):
		print('[8ball] has just been executed.')
		await ctx.defer()

		possible_answers = ['Yes.', 'No.', 'Possibly.', 'Maybe.', 'The stars tell me yes.', 'The stars tell me no.', 'The stars are unsure.', 'The stars don\'t know yet.','Fuck it sure.', 'Why not.', 'Sure', 'No fuck off.', 'Lmao never.', 'Always.', 'I don\'t fucking know.', 'YEP', '10000%', 'I think so ¯\_(ツ)_/¯']

		answer = random.choice(possible_answers)


		await ctx.send(embed=discord.Embed(title='**The magic 8ball**', description=f'- {ctx.author.mention} asked: "{question}"\n- Magic 8ball says: "{answer}"', color=Color.green()))
	@eightball.error
	async def on_eightball_error(self, ctx, error: CommandOnCooldown):
		await ctx.send(embed=discord.Embed(title='**8Ball error**', description=f'> Error: {str(error)}', color=Color.red()))


####################################################################################################################################
#################################################################################################################################### 8BALL END
####################################################################################################################################



async def setup(bot):
	await bot.add_cog(General(bot))
