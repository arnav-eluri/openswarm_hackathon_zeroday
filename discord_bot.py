import os
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")


class InjectionSentinelBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Sync slash commands with Discord
        await self.tree.sync()
        print("✅ Slash commands synced!")


bot = InjectionSentinelBot()


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


@bot.tree.command(
    name="scan",
    description="Scan a GitHub Pull Request"
)
async def scan(interaction: discord.Interaction, pr_url: str):
    await interaction.response.send_message(
        f"🚀 Injection Sentinel started!\n\nScanning:\n{pr_url}"
    )


bot.run(TOKEN)