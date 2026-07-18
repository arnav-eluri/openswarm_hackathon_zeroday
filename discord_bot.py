import os
import sys

# Ensure stdout uses UTF-8 to prevent emoji crash on Windows PM2
sys.stdout.reconfigure(encoding='utf-8')

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


import threading

async def async_execute_pipeline(target_url):
    """Bridge a synchronous generator to an async loop using a queue and a background thread."""
    loop = asyncio.get_running_loop()
    q = asyncio.Queue()

    def run_sync():
        try:
            for update in execute_pipeline(target_url):
                asyncio.run_coroutine_threadsafe(q.put(update), loop)
        except Exception as e:
            asyncio.run_coroutine_threadsafe(q.put(e), loop)
        finally:
            asyncio.run_coroutine_threadsafe(q.put(None), loop)

    threading.Thread(target=run_sync, daemon=True).start()

    while True:
        item = await q.get()
        if item is None:
            break
        if isinstance(item, Exception):
            raise item
        yield item

@bot.tree.command(name="scan", description="Scan a GitHub Pull Request for Prompt Injections")
async def scan(interaction: discord.Interaction, pr_url: str):
    # Defer the response since we will be doing work that takes longer than 3 seconds
    await interaction.response.defer(thinking=True)
    
    initial_msg = f"🚀 **Injection Sentinel Started**\n\n**Target:** {pr_url}\n\n**Status:**\n🟡 Acquiring Repository..."
    
    # We edit the deferred response message
    message = await interaction.edit_original_response(content=initial_msg)
    
    # 1. Execute Pipeline and stream updates (running in background thread to prevent heartbeat block!)
    report_markdown = None
    try:
        async for update in async_execute_pipeline(pr_url):
            if update["step"] == 7:
                report_markdown = update.get("report")
                break
                
            new_content = f"🚀 **Injection Sentinel Progress**\n\n**Target:** {pr_url}\n\n**Status:**\n{update['message']}"
            await interaction.edit_original_response(content=new_content)
            await asyncio.sleep(1.0) # Small delay to prevent discord rate limits
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