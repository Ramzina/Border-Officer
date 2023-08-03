import os
import ctypes
import time
from datetime import datetime
from discord.ext import commands
from discord import Color
from discord.ext.commands import Bot
import discord
from discord import ui
import asyncio
import pkgutil
import aiosqlite
from commands.Ticketing import TrashOpenAndTranscriptButton, CloseButton,CreateButton
from discord import app_commands
from discord.app_commands import AppCommandError

intents = discord.Intents.all()
bot = Bot(
	command_prefix="b.",
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
	bot.add_view(CreateButton())

@bot.event
async def on_member_join(member):
	guild = member.guild

	db = await aiosqlite.connect("config.db")
	await db.execute(
		"""CREATE TABLE IF NOT EXISTS welcome(guild_name STRING, guild_id INTEGER, channel_id INTEGER, toggle STRING)"""
	)

	cur = await db.execute("SELECT * FROM welcome WHERE guild_id = ?", (guild.id,))
	row = await cur.fetchone()
	if row is None:
		res = await cur.execute(
			"""
							INSERT INTO welcome VALUES
							(?, ?, ?, ?)
							""",
			(
				guild.name,
				guild.id,
				None,
				"False",
			),
		)

		await db.commit()

	res = await cur.execute(
		f"""SELECT toggle FROM welcome WHERE guild_id = {guild.id}"""
	)
	toggle = await res.fetchone()

	if toggle[0] == "True":
		res = await cur.execute(
			f"""SELECT channel_id FROM welcome WHERE guild_id = {guild.id}"""
		)
		channel = await res.fetchone()

		embed = discord.Embed(
			title="! ** • __JOIN__ • ** !",
			description=f"- {member.mention} has joined {guild.name}!\n- Member count: {guild.member_count}",
			timestamp=datetime.utcnow(),
			color=Color.from_rgb(27, 152, 250),
		)
		embed.set_footer(text='Border hopping hispanic')

		chan = bot.get_channel(channel[0])
		await chan.send(embed=embed.set_thumbnail(url=member.avatar.url))

	cur = await db.execute("""SELECT role_id FROM joinroles WHERE guild_id = ?""", (member.guild.id, ))

	role = await cur.fetchone()

	if role is None:
		return    

	join_role = guild.get_role(role[0]) 
	cur = await db.execute("""SELECT toggle FROM joinroles WHERE guild_id = ?""", (member.guild.id, ))
	tog = await cur.fetchone()
	if tog[0] != 'True':
		return
	else:
		await member.add_roles(join_role)
	return


@bot.event
async def on_member_remove(member: discord.Member):
	guild = member.guild

	db = await aiosqlite.connect("config.db")
	await db.execute(
		"""CREATE TABLE IF NOT EXISTS welcome(guild_name STRING, guild_id INTEGER, channel_id INTEGER, toggle STRING)"""
	)

	cur = await db.execute("SELECT * FROM welcome WHERE guild_id = ?", (guild.id,))
	row = await cur.fetchone()
	if row is None:
		res = await cur.execute(
			"""
							INSERT INTO welcome VALUES
							(?, ?, ?, ?)
							""",
			(
				guild.name,
				guild.id,
				None,
				"False",
			),
		)

		await db.commit()

	res = await cur.execute(
		f"""SELECT toggle FROM welcome WHERE guild_id = {guild.id}"""
	)
	toggle = await res.fetchone()

	if toggle[0] == "True":
		res = await cur.execute(
			f"""SELECT channel_id FROM welcome WHERE guild_id = {guild.id}"""
		)
		channel = await res.fetchone()

		join = bot.get_channel(channel[0])

		embed = discord.Embed(
			title="! ** • __LEAVE__ • ** !",
			description=f"- {member.mention} has left {guild.name}!\n- Member count: {guild.member_count}",
			timestamp=datetime.utcnow(),
			color=Color.from_rgb(27, 152, 250),
		)
		embed.set_footer(text='Border hopping hispanic')

		await join.send(embed=embed.set_thumbnail(url=member.avatar.url))     

		return


@bot.tree.command(name="uptime", description="Shows the uptime of the bot.")
@commands.cooldown(1, 10, commands.BucketType.user)
async def uptime(interaction: discord.Interaction):
	await interaction.response.defer(ephemeral=True)

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

	await interaction.followup.send(
		embed=embed, ephemeral=True
	)


@bot.event
async def on_reaction_add(reaction, user):
	if (
		str(reaction.message.author) == "Border Officer#0283"
		and str(reaction) == "👌"
		and user.bot == False
	):
		await reaction.message.delete()


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
async def syncit(
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


# 	ret = 0
# 	for guild in guilds:
# 		try:
# 			await ctx.bot.tree.sync(guild=guild)
# 		except discord.HTTPException:
# 			pass
# 		else:
# 			ret += 1

# 	await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")


@bot.tree.command(name="sync", description="Syncs all commands")
@commands.guild_only()
@commands.is_owner()
async def sync(interaction: discord.Interaction, spec: Optional[Literal["~", "*", "^"]] = None) -> None:
		await interaction.response.defer(ephemeral=True, thinking=True)
		if spec == "~":
			synced = await interaction.bot.tree.sync(guild=interaction.guild)
		elif spec == "*":
			interaction.bot.tree.copy_global_to(guild=interaction.guild)
			synced = await interaction.bot.tree.sync(guild=interaction.guild)
		elif spec == "^":
			interaction.bot.tree.clear_commands(guild=interaction.guild)
			print("Cleared commands!")
			await interaction.bot.tree.sync(guild=interaction.guild)
			synced = []
		else:
			await interaction.followup.send(embed=discord.Embed(title='**Sync**',description="> Sync: Beginning",color=Color.yellow()), ephemeral=True)
			synced = await interaction.client.tree.sync()

		await interaction.edit_original_response(embed=discord.Embed(title='**Sync**',description=f"> Synced: {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}", color=Color.green()))
		return



#############################################################################


@bot.tree.command(name="reload", description="Reloads a cog")
async def reload(interaction: discord.Interaction, cog: Literal["Botsetup", "Community", "General", "Help", "Moderation", "Ticketing"]):
	cog1 = cog + ".py"
	print("[Reload] has just been executed!")
	await interaction.response.defer(ephemeral=True, thinking=True)
	if cog1 in os.listdir("./commands"):
		try:
			await interaction.followup.send(embed=discord.Embed(
				title='**Reload**',
				description=f"> Reloading: {cog}",color=Color.yellow()), ephemeral=True
			)
			await interaction.client.reload_extension(f"commands.{cog}")
			await interaction.edit_original_response(embed=discord.Embed(
				title='**Reload**',
				description=f"> Reloaded: {cog}",color=Color.green())
			)
		except commands.ExtensionNotLoaded:
			await interaction.edit_original_response(embed=discord.Embed(
				title='**Reload**',
				description=f"> Error: {cog} is not loaded. Try /load",color=Color.red())
			)
	else:
		await interaction.followup.send(embed=discord.Embed(
			title='**Reload**',
			description=f"> Error: {cog} is not a valid cog",color=Color.red()), ephemeral=True
		)


@app_commands.command(name="load", description="Loads a cog")
async def load(interaction: discord.Interaction, cog: Literal["Botsetup", "Community", "General", "Help", "Moderation", "Ticketing"]):
	cog1 = cog + ".py"
	print("[Load] has just been executed!")
	await interaction.response.defer(ephemeral=True, thinking=True)
	if cog1 in os.listdir("./commands"):
		try:
			await interaction.followup.send(embed=discord.Embed(
				title='**Load**',
				description=f"> Loading: {cog}",color=Color.yellow()), ephemeral=True
			)
			await interaction.bot.load_extension(f"commands.{cog}")
			await interaction.edit_original_response(embed=discord.Embed(
				title='**Load**',
				description=f"> Loaded: {cog}",color=Color.green())
			)
		except commands.ExtensionAlreadyLoaded:
			await interaction.edit_original_response(embed=discord.Embed(
				title='**Load**',
				description=f"> Error: {cog} is already loaded. Try /reload",color=Color.red()))
	else:
		await interaction.followup.send(embed=discord.Embed(
			title='**Load**',
			description=f"> Error: {cog} is not a valid cog",color=Color.red()), ephemeral=True
		)


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



async def load():

	loaded = []

	for filename in os.listdir("./commands"):
		if filename.endswith(".py"):
			await bot.load_extension(f"commands.{filename[:-3]}")
			loaded.append(f"{filename[:-3].capitalize()}")
	print(f"Loaded (): {', '.join(loaded)}")


async def main():
	await load()


asyncio.run(main())
token = os.environ.get("TOKEN")
bot.run(token)
