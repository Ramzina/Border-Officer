from discord import Color
import discord
from discord import ui
from discord.interactions import Interaction
import python_weather
import random
from gifs.gifs import bonk_gifs
from gifs.gifs import cookie_gifs
from gifs.gifs import beer_gifs
from gifs.gifs import pizza_gifs
from gifs.gifs import coffee_gifs
import aiohttp
import asyncio
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
	@commands.has_permissions(manage_messages=True)
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
			await msg.edit(embed=discord.Embed(title=f'**Weather in {city.capitalize()}**', description=f"> ☁️ Weather: {weather.current.description}\n> 🌥️ Temperature: {weather.current.temperature}C°\n> 💦 Humidity: {weather.current.humidity}%\n> 🚩 Wind speed: {weather.current.wind_speed} Km/h\n> 🚩 Wind direction: {weather.current.wind_direction}",
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

	@commands.hybrid_command(name='bonk', description='Horni bonk someone.')
	@commands.cooldown(1,15, commands.BucketType.user)
	async def bonk(self,ctx,member:discord.Member):
		print('[Bonk] has just been executed.')
		await ctx.defer()

		gif = random.choice(bonk_gifs)

		await ctx.send(embed=discord.Embed(description=f'{ctx.author.mention} bonked {member.mention}', color=Color.blurple()).set_image(url=gif))
	@bonk.error
	async def on_bonk_error(self, ctx, error):
		await ctx.send(embed=discord.Embed(title='**Bonk error**', description=f'> Error: {str(error)}', color=Color.red()))

	@commands.hybrid_command(name='cookie', description='Gives someone a cookie.')
	@commands.cooldown(1,15, commands.BucketType.user)
	async def cookie(self,ctx,member:discord.Member):
		print('[Cookie] has just been executed.')
		await ctx.defer()

		gif = random.choice(cookie_gifs)

		await ctx.send(embed=discord.Embed(description=f'{member.mention}, {ctx.author.mention} gave you cookies!', color=Color.blurple()).set_image(url=gif))
	@cookie.error
	async def on_cookie_error(self, ctx, error):
		await ctx.send(embed=discord.Embed(title='**Cookie error**', description=f'> Error: {str(error)}', color=Color.red()))

	@commands.hybrid_command(name='beer', description='Gives someone a cold beer.')
	@commands.cooldown(1,15, commands.BucketType.user)
	async def beer(self,ctx,member:discord.Member):
		print('[Beer] has just been executed.')
		await ctx.defer()

		gif = random.choice(beer_gifs)

		await ctx.send(embed=discord.Embed(description=f'{member.mention}, {ctx.author.mention} gave you a beer!', color=Color.blurple()).set_image(url=gif))
	@beer.error
	async def on_beer_error(self, ctx, error):
		await ctx.send(embed=discord.Embed(title='**Beer error**', description=f'> Error: {str(error)}', color=Color.red()))

	@commands.hybrid_command(name='emojirob', description='Robs the image of an emoji that you enter.')
	@commands.cooldown(1,15, commands.BucketType.user)
	async def emojirob(self, ctx, emoji:discord.PartialEmoji):
		await ctx.defer()

		msg = await ctx.send(embed=discord.Embed(description='<:yellowdot:1148198566448337018> Stealing emoji...', color=Color.yellow()))

		num = random.randint(2,7)
		floatnum = num / 10

		await asyncio.sleep(floatnum)

		await msg.edit(embed=discord.Embed(description='<:greentick:1148198571330515025> Emoji image stolen.', color=Color.green()).set_image(url=emoji.url))
	@emojirob.error
	async def on_emojirob_error(self, ctx, error):
		await ctx.send(embed=discord.Embed(title='**Emojirob error**', description=f'> Error: {str(error)}', color=Color.red()))

	@commands.hybrid_command(name='avatar', description='Gets the avatar of a user.')
	@commands.cooldown(1,15, commands.BucketType.user)
	async def avatar(self, ctx, user:discord.User=None):
		await ctx.defer()

		msg = await ctx.send(embed=discord.Embed(description=f'<:yellowdot:1148198566448337018> Fetching avatar...', color=Color.yellow()))

		num = random.randint(2,7)
		floatnum = num / 10

		await asyncio.sleep(floatnum)
		if user is None:
			await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Your avatar.', color=Color.green()).set_image(url=ctx.author.avatar.url))
			return
		await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> {user.mention}\'s Avatar.', color=Color.green()).set_image(url=user.avatar.url))
	@avatar.error
	async def on_avatar_error(self, ctx, error):
		await ctx.send(embed=discord.Embed(title='**Avatar error**', description=f'> Error: {str(error)}', color=Color.red()))

	@commands.hybrid_command(name='emojisteal', description='Steals an emoji that you enter and adds it to the guild.')
	@commands.has_permissions(manage_emojis=True)
	@commands.cooldown(1,15, commands.BucketType.user)
	async def emojisteal(self, ctx, emoji:discord.PartialEmoji, *,name):
		await ctx.defer()

		msg = await ctx.send(embed=discord.Embed(description='<:yellowdot:1148198566448337018> Stealing emoji...', color=Color.yellow()))

		num = random.randint(2,7)
		floatnum = num / 10

		await asyncio.sleep(floatnum)

		await msg.edit(embed=discord.Embed(description='<:yellowdot:1148198566448337018> Emoji stolen, adding emoji...', color=Color.yellow()))

		emojj = await ctx.guild.create_custom_emoji(name=name, image=await emoji.read())
		await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Emoji stolen and added. {emojj}', color=Color.green()))
	@emojisteal.error
	async def on_emojisteal_error(self, ctx, error):
		await ctx.send(embed=discord.Embed(title='**Emojisteal error**', description=f'> Error: {str(error)}', color=Color.red()))
	
	@commands.hybrid_command(name='emojiadd', description='Adds an emoji to the guild with a name you chose.')
	@commands.cooldown(1,15, commands.BucketType.user)
	async def emojiadd(self, ctx,url, *,name):
		await ctx.defer()

		async with aiohttp.ClientSession() as cs:
			async with cs.get(url) as res:

				data = await res.read()

		msg = await ctx.send(embed=discord.Embed(description='<:yellowdot:1148198566448337018> Adding emoji...', color=Color.yellow()))

		num = random.randint(2,7)
		floatnum = num / 10

		await asyncio.sleep(floatnum)

		emojj = await ctx.guild.create_custom_emoji(name=name, image=data)
		await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Emoji added. {emojj}', color=Color.green()))
	@emojiadd.error
	async def on_emojiadd_error(self, ctx, error):
		await ctx.send(embed=discord.Embed(title='**Emojiadd error**', description=f'> Error: {str(error)}', color=Color.red()))

	@commands.hybrid_command(name='coffee', description='Gives someone a hot coffee.')
	@commands.cooldown(1,15, commands.BucketType.user)
	async def coffee(self,ctx,member:discord.Member):
		print('[Coffee] has just been executed.')
		await ctx.defer()

		gif = random.choice(coffee_gifs)

		await ctx.send(embed=discord.Embed(description=f'{member.mention}, {ctx.author.mention} gave you coffee!', color=Color.blurple()).set_image(url=gif))
	@coffee.error
	async def on_coffee_error(self, ctx, error):
		await ctx.send(embed=discord.Embed(title='**Coffee error**', description=f'> Error: {str(error)}', color=Color.red()))

	@commands.hybrid_command(name='pizza', description='Gives someone a warm pizza.')
	@commands.cooldown(1,15, commands.BucketType.user)
	async def pizza(self,ctx,member:discord.Member):
		print('[Pizza] has just been executed.')
		await ctx.defer()

		gif = random.choice(pizza_gifs)

		await ctx.send(embed=discord.Embed(description=f'{member.mention}, {ctx.author.mention} gave you pizza!', color=Color.blurple()).set_image(url=gif))
	@pizza.error
	async def on_pizza_error(self, ctx, error):
		await ctx.send(embed=discord.Embed(title='**Pizza error**', description=f'> Error: {str(error)}', color=Color.red()))


async def setup(bot):
	await bot.add_cog(General(bot))
