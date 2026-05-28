import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
from src.utils.downloader import MusicDownloader
from src.utils.uploader import Top4TopUploader
from src.utils.queue_manager import QueueManager

class UploaderCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.queue_manager = QueueManager()
        
        self.ydl_opts = {
            'format': 'bestaudio',
            'ffmpeg_location': r'',
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'noplaylist': True,
        }

    @app_commands.command(name="upload", description="Download audio from YouTube and upload to Top4Top")
    @app_commands.describe(url="Paste the YouTube link here")
    async def upload(self, interaction: discord.Interaction, url: str):
        await interaction.response.defer()
        
        async def process_task():
            message = None
            try:
                embed_start = discord.Embed(
                    title="`⏳` Processing Request",
                    description=f"Initiating download sequence for:\n**{url}**\n\n`🔎` Searching metadata...\n`📡` Connecting to YouTube servers...",
                    color=discord.Color.blue()
                )
                message = await interaction.followup.send(embed=embed_start)

                try:
                    file_path, title, duration, uploader, file_size = await MusicDownloader.download_audio(url, self.ydl_opts)
                    
                    size_mb = file_size / (1024 * 1024) if file_size else 0
                    size_str = f"{size_mb:.2f} MB" if size_mb > 0 else "Unknown"
                    mins, secs = divmod(duration, 60)
                    duration_str = f"{int(mins)}:{int(secs):02d}"

                except Exception as e:
                    await message.edit(embed=discord.Embed(title="`❌` Download Error", description=f"Download failed: `{str(e)}`", color=discord.Color.red()))
                    return

                embed_uploading = discord.Embed(
                    title="`📤` Uploading to Top4Top",
                    description=f"**Title:** `{title}`\n**Artist:** `{uploader}`\n**Duration:** `{duration_str}`\n**Size:** `{size_str}`\n\n`🚀` Converting & Uploading...",
                    color=discord.Color.orange()
                )
                await message.edit(embed=embed_uploading)

                download_link = None
                try:
                    download_link = await Top4TopUploader.upload_file(file_path)
                except Exception as e:
                    await message.edit(embed=discord.Embed(title="`❌` Upload Error", description=f"Upload failed: `{str(e)}`", color=discord.Color.red()))
                    MusicDownloader.cleanup_file(file_path)
                    return

                MusicDownloader.cleanup_file(file_path)

                embed_success = discord.Embed(
                    title="`✅` Upload Success!",
                    color=discord.Color.green()
                )
                embed_success.add_field(name="`🎵` Title", value=f"`{title}`", inline=False)
                embed_success.add_field(name="`👤` Uploader", value=f"`{uploader}`", inline=True)
                embed_success.add_field(name="`⏱️` Duration", value=f"`{duration_str}`", inline=True)
                embed_success.add_field(name="`📦` Size", value=f"`{size_str}`", inline=True)
                embed_success.add_field(name="`🔗` Direct Link", value=f"[Click to Download]({download_link})", inline=False)
                embed_success.set_footer(text="Uploaded via Discord Bot • Top4Top.io")

                content_msg = f"**Download Link:** {download_link}"
                await message.edit(content=content_msg, embed=embed_success)

            except Exception as e:
                try:
                    await interaction.followup.send(f"An unexpected error occurred: `{str(e)}`")
                except:
                    pass

        await self.queue_manager.add_task(process_task())

async def setup(bot: commands.Bot):
    await bot.add_cog(UploaderCog(bot))