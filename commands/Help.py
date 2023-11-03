import discord
import asyncio
import aiosqlite
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from discord.ui import View, Select
from discord import Color

class HelpSelect(Select):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            placeholder="Choose a command category",
            options=[
                discord.SelectOption(label=cog_name, description=cog.__doc__)
                for cog_name, cog in bot.cogs.items()
                if cog.__cog_commands__ or cog.__cog_app_commands__
                and cog_name not in ["HelpSelect", "Help"]
            ],
        )

        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        cog = self.bot.get_cog(self.values[0])
        assert cog

        commands_mixer = []
        for i in cog.walk_app_commands():
            commands_mixer.append(i)
        for i in cog.walk_commands():
            commands_mixer.append(i)

        embed = discord.Embed(
            title=f"{cog.__cog_name__} Commands",
            description="\n".join(
                f"**{self.bot.command_prefix}{command.name}:** `{command.description}`"
                for command in commands_mixer
            ),
            color=Color.blurple(),
        ).set_footer(
            text=f"{len(commands_mixer)} {cog.__cog_name__} Commands"
        )

        view = View().add_item(HelpSelect(self.bot))
        await interaction.response.edit_message(embed=embed, view=view)

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="Get the basic help for commands")
    async def help(self, ctx):
        embed = discord.Embed(
            title="Help Command",
            description="Choose a slash command category you need help for",
            color=Color.blurple(),
        ).set_footer(text='This will be deleted in 30 seconds.')

        view = View().add_item(HelpSelect(self.bot))
        msg = await ctx.send(embed=embed, view=view)
        await asyncio.sleep(30)
        await msg.delete()

async def setup(bot):
    await bot.add_cog(HelpSelect(bot))
    
async def setup(bot):
    await bot.add_cog(Help(bot))
