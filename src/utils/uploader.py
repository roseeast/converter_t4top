import aiohttp
from bs4 import BeautifulSoup
import os

class Top4TopUploader:
    BASE_URL = "https://top4top.io/"
    UPLOAD_URL = "https://top4top.io/index.php"

    @staticmethod
    async def upload_file(file_path: str):
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(Top4TopUploader.BASE_URL) as response:
                    if response.status != 200:
                        raise Exception(f"Failed to fetch homepage: {response.status}")
                    html = await response.text()
            except Exception as e:
                raise Exception(f"Error connecting to Top4Top: {str(e)}")

            soup = BeautifulSoup(html, 'html.parser')
            sid_input = soup.find('input', {'name': 'sid'})
            
            if not sid_input:
                raise Exception("Could not find session ID (sid) on the page. The site might have changed.")
            
            sid = sid_input['value']
            
            data = aiohttp.FormData()
            data.add_field('sid', sid)
            data.add_field('submitr', '[ رفع الملفات ]')
            
            with open(file_path, 'rb') as f:
                data.add_field('file_1_', f, filename=os.path.basename(file_path))
                
                try:
                    async with session.post(Top4TopUploader.UPLOAD_URL, data=data) as upload_response:
                        if upload_response.status != 200:
                            raise Exception(f"Upload failed with status: {upload_response.status}")
                        result_html = await upload_response.text()
                except Exception as e:
                    raise Exception(f"Error during file upload: {str(e)}")

            result_soup = BeautifulSoup(result_html, 'html.parser')
            
            download_link = None
            
            for textarea in result_soup.find_all(['textarea', 'input']):
                val = textarea.get('value') or textarea.text
                if val and 'top4top.io' in val and 'http' in val:

                    if '[url' not in val and '<a href' not in val:
                        download_link = val.strip()
                        break
            
            if not download_link:
                 for a in result_soup.find_all('a', href=True):
                     if 'top4top.io/p_' in a['href'] or 'top4top.io/m_' in a['href']:
                         download_link = a['href']
                         break

            if not download_link:
                raise Exception("Upload successful, but could not parse the download link.")

            return download_link
