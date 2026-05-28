import discord
from discord.ext import commands
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()

class Bot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=intents,
            help_command=None
        )

    async def setup_hook(self):
        try:
            await self.load_extension('src.cogs.uploader_cog')
            print("Loaded uploader_cog")
        except Exception as e:
            print(f"Failed to load extension: {e}")
        
        await self.tree.sync()
        print("Synced slash commands")

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

async def main():
    if not TOKEN:
        print("Error: DISCORD_TOKEN not found in environment variables.")
        return

    bot = Bot()
    async with bot:
        await bot.start(TOKEN)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
