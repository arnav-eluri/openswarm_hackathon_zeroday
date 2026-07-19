import os
import tempfile
import asyncio
import discord
from discord import app_commands
from discord.ui import Button, View
from dotenv import load_dotenv
import git

from workflow import execute_pipeline

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

class ApprovalView(View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(label="✅ Approve", style=discord.ButtonStyle.success)
    async def approve(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Workflow Approved! Code is ready to merge.", ephemeral=False)
        self.stop()

    @discord.ui.button(label="❌ Reject", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: Button):
        await interaction.response.send_message("Workflow Rejected! Please review the prompt injection vulnerabilities.", ephemeral=False)
        self.stop()


class InjectionSentinelBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Slash commands synced!")


bot = InjectionSentinelBot()


@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")


@bot.tree.command(name="scan", description="Scan a GitHub Pull Request for Prompt Injections")
async def scan(interaction: discord.Interaction, pr_url: str):
    # Defer the response since we will be doing work that takes longer than 3 seconds
    await interaction.response.defer(thinking=True)
    
    initial_msg = f"🚀 **Injection Sentinel Started**\n\n**Target:** {pr_url}\n\n**Status:**\n🟡 Cloning Repository..."
    
    # We edit the deferred response message
    message = await interaction.edit_original_response(content=initial_msg)
    
    # 1. Clone repository to temp directory
    try:
        temp_dir = tempfile.mkdtemp()
        if "github.com" in pr_url:
            repo_url = pr_url.split("/pull/")[0] + ".git"
            git.Repo.clone_from(repo_url, temp_dir)
        else:
            await interaction.edit_original_response(content="🔴 **Error:** Please provide a valid GitHub Pull Request URL.")
            return
    except Exception as e:
        await interaction.edit_original_response(content=f"🔴 **Error cloning repository:** {str(e)}")
        return

    # 2. Execute Pipeline and stream updates
    report_markdown = None
    try:
        for update in execute_pipeline(temp_dir, pr_url):
            if update["step"] == 7:
                report_markdown = update.get("report")
                break
                
            new_content = f"🚀 **Injection Sentinel Progress**\n\n**Target:** {pr_url}\n\n**Status:**\n{update['message']}"
            await interaction.edit_original_response(content=new_content)
            await asyncio.sleep(1.5) # Fake delay for visualization effect
    except Exception as e:
         await interaction.edit_original_response(content=f"🔴 **Pipeline Error:** {str(e)}")
         return
         
    # 3. Send final report
    if report_markdown:
        await interaction.edit_original_response(content="✅ **Scan Complete**")
        
        embed = discord.Embed(title="🚨 Injection Sentinel Report", color=0xff0000)
        embed.description = report_markdown
        
        view = ApprovalView()
        # Followup to attach the embed and view
        await interaction.followup.send(embed=embed, view=view)


if __name__ == "__main__":
    if TOKEN:
        bot.run(TOKEN)
    else:
        print("Please set DISCORD_TOKEN in .env file.")