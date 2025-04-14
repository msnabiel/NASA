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
title = re.sub(r'[^\w\s-]', '', data['title'])  # Remove special chars
title = title.strip().replace(" ", "-")         # Replace spaces with hyphens
explanation = data['explanation']
media_type = data['media_type']
url = data['url']

# === FORMAT DATE & FOLDER NAME ===
date_obj = datetime.strptime(date, "%Y-%m-%d")
formatted_date = date_obj.strftime("%d-%m-%y")
folder_name = f"{formatted_date}-{title}"
os.makedirs(folder_name, exist_ok=True)

thumbnail_url = None  # Init

# === HANDLE MEDIA ===
if media_type == 'image':
    img_data = requests.get(url).content
    with open(f"{folder_name}/image.jpg", 'wb') as f:
        f.write(img_data)
else:
    video_id = re.search(r"v=([a-zA-Z0-9_-]+)", url)
    if video_id:
        video_id = video_id.group(1)
        thumbnail_url = f"https://img.youtube.com/vi/{video_id}/0.jpg"
    with open(f"{folder_name}/video_link.txt", 'w') as f:
        f.write(url)

# === CLEAN EXPLANATION TEXT ===
# Move this OUTSIDE the f-string to avoid backslash error
quoted_explanation = explanation.replace('\n', '\n> ')

# === FORMAT README CONTENT ===
readme_content = (
    f"# {title}\n\n"
    f"**Date:** {formatted_date}  \n"
    f"**Media Type:** `{media_type}`  \n\n"
    f"{'![Image](image.jpg)' if media_type == 'image' else f'![Video Thumbnail]({thumbnail_url})'}\n\n"
    f"{'[Watch Video](' + url + ')' if media_type == 'video' else ''}\n\n"
    "---\n\n"
    "### Explanation\n\n"
    f"> {quoted_explanation}\n\n"
    "---\n\n"
    "[View this on NASA APOD](https://apod.nasa.gov/apod/astropix.html)\n"
)

# === WRITE README ===
with open(f"{folder_name}/README.md", 'w', encoding='utf-8') as f:
    f.write(readme_content)
