import requests
import os
from datetime import datetime
import re

# === CONFIG ===
API_KEY = os.getenv('NASA_API_KEY')  # Fetch API key from environment variable
if not API_KEY:
    raise ValueError("NASA API Key is not set as an environment variable.")
URL = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}"

# === FETCH DATA ===
res = requests.get(URL)
data = res.json()

date = data['date']
title = data['title'].replace("/", "-")  # Clean title
explanation = data['explanation']
media_type = data['media_type']
url = data['url']

folder_name = f"{date} - {title}"
os.makedirs(folder_name, exist_ok=True)

# === HANDLE IMAGE ===
if media_type == 'image':
    img_data = requests.get(url).content
    with open(f"{folder_name}/image.jpg", 'wb') as f:
        f.write(img_data)
else:
    # === HANDLE VIDEO ===
    video_id = re.search(r"v=([a-zA-Z0-9_-]+)", url)
    if video_id:
        video_id = video_id.group(1)
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
        with open(f"{folder_name}/video_link.txt", 'w') as f:
            f.write(url)

# === CREATE README.md ===
readme_content = f"""# {title}

**Date:** {date}  
**Media Type:** {media_type}  

"""
if media_type == "image":
    readme_content += f"![Image]({url})\n"
else:
    readme_content += f"![Video Thumbnail]({thumbnail_url})\n"
    readme_content += f"Video Link: {url}\n"

readme_content += f"""
**Explanation:**  
{explanation}

[View on NASA APOD](https://apod.nasa.gov/apod/astropix.html)
"""

with open(f"{folder_name}/README.md", 'w', encoding='utf-8') as f:
    f.write(readme_content)
