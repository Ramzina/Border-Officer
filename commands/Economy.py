import discord
from discord.ext import commands
import asyncio
from discord import Color
import random
import aiosqlite

class Economy(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.hybrid_command(name='givecash', description='Gives cash to a member.')
	@commands.has_permissions(administrator=True)
	async def givecash(self, ctx, member: discord.Member, cash:int=500):
		await ctx.defer()

		db = await aiosqlite.connect("Economy.db")
		await db.execute("CREATE TABLE IF NOT EXISTS money(guild_name STRING, guild_id INTEGER, user_id INTEGER, cash INTEGER, bank INTEGER)")

		cur = await db.execute("SELECT user_id, cash FROM money WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, ctx.author.id, ))
		res = await cur.fetchall()


		if not res:
			await db.execute("INSERT INTO money(guild_name, guild_id, user_id, cash, bank) VALUES(?,?,?,?,?)", (ctx.guild.name, ctx.guild.id, member.id, cash, 0, ))
			await db.commit()
			await ctx.send(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Cash given to {member.mention}: {cash}', color=Color.green()))
			return
		ress = res[0]
		usercash = ress[1]
		newcash = usercash + cash
		await db.execute("UPDATE money SET cash = ? WHERE guild_id = ? AND user_id = ?", (newcash, ctx.guild.id, member.id, ))
		await db.commit()
		await ctx.send(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Cash given to {member.mention}: {cash}', color=Color.green()))
		await db.close()

	@givecash.error
	async def on_givecash_error(
		self, ctx, error
	):
		await ctx.send(embed=discord.Embed(title='**Givecash Error**', description=f'> Error: {str(error)}', color=Color.red()))

	@commands.hybrid_command(name='bal', description='Tells you the money in your wallet and bank.')
	async def bal(self, ctx):
		await ctx.defer()
		msg = await ctx.send(embed=discord.Embed(description=f'<:yellowdot:1148198566448337018> Fetching balance.', color=Color.yellow()))
		db = await aiosqlite.connect("Economy.db")
		await db.execute("CREATE TABLE IF NOT EXISTS money(guild_name STRING, guild_id INTEGER, user_id INTEGER, cash INTEGER, bank INTEGER)")

		cur = await db.execute("SELECT cash, bank FROM money WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, ctx.author.id, ))
		res = await cur.fetchall()
		print(res)

		if not res:
			await msg.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Error: You have no money. Try {self.bot.command_prefix}beg', color=Color.red()))
			return
		ress = res[0]
		await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Wallet: {ress[0]}, Bank: {ress[1]}', color=Color.green()))
		await db.close()
	@bal.error
	async def on_bal_error(
		self, ctx, error
	):
		await ctx.send(embed=discord.Embed(title='**Cash Error**', description=f'> Error: {str(error)}', color=Color.red()))

	@commands.hybrid_command(name='dep', description='Deposits money into your bank.')
	async def dep(self, ctx, amount:str):
		await ctx.defer()
		msg = await ctx.send(embed=discord.Embed(description=f'<:yellowdot:1148198566448337018> Depositing cash.', color=Color.yellow()))
		db = await aiosqlite.connect("Economy.db")
		await db.execute("CREATE TABLE IF NOT EXISTS money(guild_name STRING, guild_id INTEGER, user_id INTEGER, cash INTEGER, bank INTEGER)")

		cur = await db.execute("SELECT cash, bank FROM money WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, ctx.author.id, ))
		res = await cur.fetchall()

		if not res:
			await msg.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Error: You have no money.', color=Color.red()))
			return
		ress = res[0]
		if str(amount.lower()) == 'all':
				
				await db.execute("UPDATE money SET bank = ?, cash = ? WHERE guild_id = ? AND user_id = ?", (ress[1] + ress[0], ress[0] - ress[0], ctx.guild.id, ctx.author.id))
				await db.commit()
				await db.close()
				await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Deposited: {ress[0]}', color=Color.green()))
				return
		if ress[0] >= int(amount):
			await db.execute("UPDATE money SET cash = ?, bank = ? WHERE guild_id = ? AND user_id = ?", (ress[0] - int(amount), ress[1] + int(amount), ctx.guild.id, ctx.author.id))
			await db.commit()
			await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Deposited: {amount}', color=Color.green()))
			await db.close()
			return
		if ress[0] < int(amount):
			await msg.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Error: You don\'t have enough money.', color=Color.red()))
			await db.close()
			return

#	@dep.error
#	async def on_dep_error(
#		self, ctx, error
#	):
#		await ctx.send(embed=discord.Embed(title='**Dep Error**', description=f'> Error: {str(error)}', color=Color.red()))

	@commands.hybrid_command(name='withdraw', description='Withdraws money from your bank.')
	async def withdraw(self, ctx, amount:str):
		await ctx.defer()
		msg = await ctx.send(embed=discord.Embed(description=f'<:yellowdot:1148198566448337018> Withdrawing cash.', color=Color.yellow()))
		db = await aiosqlite.connect("Economy.db")
		await db.execute("CREATE TABLE IF NOT EXISTS money(guild_name STRING, guild_id INTEGER, user_id INTEGER, cash INTEGER, bank INTEGER)")

		cur = await db.execute("SELECT bank, cash FROM money WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, ctx.author.id, ))
		res = await cur.fetchall()

		if not res:
			await msg.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Error: You have no money.', color=Color.red()))
			return
		ress = res[0]
		if str(amount.lower()) == 'all':
			await db.execute("UPDATE money SET bank = ?, cash = ? WHERE guild_id = ? AND user_id = ?", (0, ress[1] + ress[0], ctx.guild.id, ctx.author.id))
			await db.commit()
			await db.close()
			await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Withdrew: {ress[0]}', color=Color.green()))
			return
		if ress[0] >= int(amount):
			await db.execute("UPDATE money SET bank = ?, cash = ? WHERE guild_id = ? AND user_id = ?", (ress[0] - int(amount), ress[1] + int(amount), ctx.guild.id, ctx.author.id))
			await db.commit()
			await db.close()
			await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Withdrew: {amount}', color=Color.green()))
			return
		if ress[0] < int(amount):
			await msg.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Error: You don\'t have enough banked money.', color=Color.red()))
			await db.close()
			return

	@withdraw.error
	async def on_withdraw_error(
		self, ctx, error
	):
		await ctx.send(embed=discord.Embed(title='**Withdraw Error**', description=f'> Error: {str(error)}', color=Color.red()))

	@commands.hybrid_command(name='coinflip', description='Double or nothing on a bet you place!')
	async def coinflip(self, ctx, hot:str,cash:int=500):
		await ctx.defer()
		msg = await ctx.send(embed=discord.Embed(description=f'<:yellowdot:1148198566448337018> Flipping coin.', color=Color.yellow()))
		db = await aiosqlite.connect("Economy.db")
		await db.execute("CREATE TABLE IF NOT EXISTS money(guild_name STRING, guild_id INTEGER, user_id INTEGER, cash INTEGER, bank INTEGER)")

		cur = await db.execute("SELECT cash FROM money WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, ctx.author.id, ))
		res = await cur.fetchone()

		if not res:
			await msg.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Error: You have no money.', color=Color.red()))
			return
		print(res[0])
		sides = ['Heads', 'Tails']
		if hot.capitalize() not in sides:
			await msg.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Error: {hot} is not a side of a coin, choose heads or tails.', color=Color.red()))
			return
		rside = random.choice(sides)
		print(rside)
		if res[0] >= cash:
			if rside == hot.capitalize():

				newcash = res[0] + cash * 2

				await db.execute("UPDATE money SET cash = ? WHERE guild_id = ? AND user_id = ?", (newcash, ctx.guild.id, ctx.author.id, ))
				await db.commit()
				await msg.edit(embed=discord.Embed(title=f'{rside.capitalize()}', description=f'> You won {cash * 2} cash!', color=Color.green()))
				await db.close()
			else:
				newcash = res[0] - cash

				await db.execute("UPDATE money SET cash = ? WHERE guild_id = ? AND user_id = ?", (newcash, ctx.guild.id, ctx.author.id, ))
				await db.commit()
				await msg.edit(embed=discord.Embed(title=f'{rside.capitalize()}', description=f'> You lost {cash} cash.', color=Color.red()))
				await db.close()
				return
		else:
			await msg.edit(embed=discord.Embed(description=f'<:redtick:1148198569296273408> Error: You don\'t have `{cash}` cash in your wallet.',color=Color.red()))
			await db.close()

	@coinflip.error
	async def on_coinflip_error(
		self, ctx, error
	):
		await ctx.send(embed=discord.Embed(title='**Coinflip Error**', description=f'> Error: {str(error)}', color=Color.red()))


	@commands.hybrid_command(name='beg', description='You beg for money.')
	@commands.cooldown(1,30, commands.BucketType.user)
	async def beg(self, ctx):
		await ctx.defer()
		msg = await ctx.send(embed=discord.Embed(description=f'<:yellowdot:1148198566448337018> Begging for cash.', color=Color.yellow()))
		db = await aiosqlite.connect("Economy.db")
		await db.execute("CREATE TABLE IF NOT EXISTS money(guild_name STRING, guild_id INTEGER, user_id INTEGER, cash INTEGER, bank INTEGER)")

		cur = await db.execute("SELECT cash FROM money WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, ctx.author.id, ))
		res = await cur.fetchone()

		if not res:
			beggedcash = random.randint(10,120)
			newcash = 0 + beggedcash
			await db.execute("INSERT INTO money(guild_name, guild_id, user_id, cash,bank) VALUES(?,?,?,?,?)", (ctx.guild.name,ctx.guild.id, ctx.author.id,newcash, 0))
			await db.commit()
			await db.close()
			await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Money earned: {beggedcash}', color=Color.green()))
			return
		beggedcash = random.randint(10,120)
		newcash = res[0] + beggedcash
		await db.execute("UPDATE money SET cash = ? WHERE guild_id = ? AND user_id = ?", (newcash, ctx.guild.id, ctx.author.id, ))
		await db.commit()
		await db.close()
		await msg.edit(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Money earned: {beggedcash}', color=Color.green()))
	@beg.error
	async def on_beg_error(
		self, ctx, error
	):
		await ctx.send(embed=discord.Embed(title='**Beg Error**', description=f'> Error: {str(error)}', color=Color.red()))


	@commands.hybrid_command(name='rob', description='Robs a member.')
	@commands.cooldown(1,60, commands.BucketType.user)
	async def rob(self, ctx, member: discord.Member):
		await ctx.defer()

		cash = random.randint(20, 600)

		chances = [True, False]

		successful = random.choice(chances)

		db = await aiosqlite.connect("Economy.db")
		await db.execute("CREATE TABLE IF NOT EXISTS money(guild_name STRING, guild_id INTEGER, user_id INTEGER, cash INTEGER, bank INTEGER)")

		robbing = await db.execute("SELECT cash FROM money WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, ctx.author.id, ))
		robbed = await db.execute("SELECT cash FROM money WHERE guild_id = ? AND user_id = ?", (ctx.guild.id, member.id, ))
		robbed = await robbed.fetchone()
		robbing = await robbing.fetchone()


		if not robbed or robbed[0] <= 0:
			await ctx.send(embed=discord.Embed(description=f'<:redtick:1148198569296273408> {member.mention} has no cash to rob.', color=Color.red()))
			await db.close()
			return
		
		if successful:
			usercashrobbed = robbed[0]
			newcashrobbed = usercashrobbed - cash
			if newcashrobbed <= 0:
				newcashrobbed = 0
			usercashrobbing = robbing[0]
			newcashrobbing = usercashrobbing + cash
			await db.execute("UPDATE money SET cash = ? WHERE guild_id = ? AND user_id = ?", (newcashrobbed, ctx.guild.id, member.id, ))
			await db.commit()
			await db.execute("UPDATE money SET cash = ? WHERE guild_id = ? AND user_id = ?", (newcashrobbing, ctx.guild.id, ctx.author.id, ))
			await db.commit()
			await ctx.send(embed=discord.Embed(description=f'<:greentick:1148198571330515025> Robbed {cash} from {member.mention}.', color=Color.green()))
			await db.close()
		else:
			await ctx.send(embed=discord.Embed(description=f'<:redtick:1148198569296273408> you failed robbing {member.mention}!.', color=Color.red()))
			await db.close()
			return
	@rob.error
	async def on_rob_error(
		self, ctx, error
	):
		await ctx.send(embed=discord.Embed(title='**Rob Error**', description=f'> Error: {str(error)}', color=Color.red()))


async def setup(bot):
	await bot.add_cog(Economy(bot))
