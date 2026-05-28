import yt_dlp
import os
import asyncio
from datetime import datetime

class MusicDownloader:
    DOWNLOAD_DIR = "downloads"

    @staticmethod
    def ensure_dir(directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    @staticmethod
    async def download_audio(url: str, ydl_opts_override: dict = None):
        MusicDownloader.ensure_dir(MusicDownloader.DOWNLOAD_DIR)
        
        timestamp = int(datetime.now().timestamp())
        output_template = f"{MusicDownloader.DOWNLOAD_DIR}/%(title)s_{timestamp}.%(ext)s"

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True,
            'no_warnings': True,
            'ffmpeg_location': r'',
        }
        
        if ydl_opts_override:
            ydl_opts.update(ydl_opts_override)

        loop = asyncio.get_event_loop()
        
        def run_download():
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    
                    filename = ydl.prepare_filename(info)
                    
                    if os.path.exists(filename):
                        final_filename = filename
                    else:
                        final_filename = os.path.splitext(filename)[0] + ".mp3"
                    
                    if not os.path.exists(final_filename):
                        files = [f for f in os.listdir(MusicDownloader.DOWNLOAD_DIR) 
                                if f.endswith(('.mp3', '.m4a', '.webm')) 
                                and str(timestamp) in f]
                        if files:
                            final_filename = os.path.join(MusicDownloader.DOWNLOAD_DIR, files[0])
                    
                    duration = info.get('duration', 0)
                    uploader = info.get('uploader', 'Unknown')
                    file_size = os.path.getsize(final_filename) if os.path.exists(final_filename) else info.get('filesize_approx', 0)
                    
                    return final_filename, info.get('title', 'Unknown Title'), duration, uploader, file_size
                    
            except Exception as e:
                raise Exception(f"yt-dlp error: {str(e)}")

        try:
            file_path, title, duration, uploader, file_size = await loop.run_in_executor(None, run_download)
            
            if not os.path.exists(file_path):
                raise Exception(f"File not found: {file_path}")
                
            return file_path, title, duration, uploader, file_size
            
        except Exception as e:
            raise Exception(f"Download failed: {str(e)}")

    @staticmethod
    def cleanup_file(file_path: str):
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"Cleaned up: {file_path}")
            except Exception as e:
                print(f"Error deleting file {file_path}: {e}")