import discord
import aiosqlite
from discord import app_commands
from discord.ext import commands
from datetime import datetime
from discord.ui import View, Select
from discord import Color

class HelpSelect(Select):
    def __init__(self, bot: commands.Bot):
        super().__init__(
            placeholder="Choose a category",
            options=[
                discord.SelectOption(
                    label=cog_name, description=cog.__doc__
                ) for cog_name, cog in bot.cogs.items() if cog.__cog_app_commands__ and cog_name not in ['HelpSelect', 'Help']
            ]
        )

        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        cog = self.bot.get_cog(self.values[0])
        assert cog

        commands_mixer = []
        for i in cog.walk_app_commands():
            commands_mixer.append(i)
        
        embed = discord.Embed(
            title=f"{cog.__cog_name__} Commands",
            description="\n".join(
                f"**/{command.name}:** `{command.description}`"
                for command in commands_mixer),timestamp=datetime.utcnow(),color=Color.from_rgb(27, 152, 250)).set_footer(text="Border hopping hispanic")

        view = View().add_item(HelpSelect(self.bot))
        await interaction.response.edit_message(embed=embed, view=view)

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="help", description="Get the basic help for commands")
    async def help(self, interaction: discord.Interaction):

        embed = discord.Embed(
            title="Help Command",
            description="Choose a slash command category you need help for",
            timestamp=datetime.utcnow(),
            color=Color.from_rgb(27, 152, 250),
        )

        view = View().add_item(HelpSelect(self.bot))
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


async def setup(bot):
    await bot.add_cog(HelpSelect(bot))
    
async def setup(bot):
    await bot.add_cog(Help(bot))