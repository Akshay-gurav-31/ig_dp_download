from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re
import os
import time

app = Flask(__name__)

# Folder to save downloaded DPs
DOWNLOAD_FOLDER = "static/downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# Headers to mimic a real mobile browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer": "https://www.instagram.com/",
    "Connection": "keep-alive"
}

def get_profile_pic_url(username, retries=3, delay=2):
    for attempt in range(retries):
        try:
            # Step 1: Try the internal endpoint (?__a=1)
            endpoint_url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
            response = requests.get(endpoint_url, headers=HEADERS, timeout=10)
            if response.status_code == 200:
                json_data = response.json()
                user_data = json_data.get("graphql", {}).get("user", {})
                if user_data.get("is_private"):
                    return None, "This account is private. Profile picture cannot be accessed."
                profile_pic_url = user_data.get("profile_pic_url_hd") or user_data.get("profile_pic_url")
                if profile_pic_url:
                    return profile_pic_url, None
            
            # Step 2: Fallback to scraping the mobile page
            url = f"https://www.instagram.com/{username}/?hl=en"
            response = requests.get(url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                return None, "Profile not found or inaccessible."

            # Parse the HTML with BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Check if the profile is private
            private_indicator = soup.find(string=re.compile("This Account is Private"))
            if private_indicator:
                return None, "This account is private. Profile picture cannot be accessed."

            # Try to find the profile picture in a <meta> tag
            meta_tag = soup.find("meta", property="og:image")
            if meta_tag and meta_tag.get("content"):
                return meta_tag["content"], None

            # Look for JSON data in a <script> tag
            script_tags = soup.find_all("script", type="text/javascript")
            for script in script_tags:
                if script.string and "profile_pic_url" in script.string:
                    match = re.search(r'"profile_pic_url":"(.*?)"', script.string)
                    if match:
                        return match.group(1).replace("\\/", "/"), None

            return None, "Could not find profile picture. Instagram may have changed its structure."

        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                time.sleep(delay)  # Wait before retrying
                continue
            return None, f"Failed to connect to Instagram: {str(e)}"
        except Exception as e:
            return None, f"An error occurred: {str(e)}"

@app.route("/", methods=["GET", "POST"])
def index():
    image_url = None
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            # Get the profile picture URL
            profile_pic_url, error = get_profile_pic_url(username)
            if error:
                return render_template("index.html", error=error)

            # Download the image
            try:
                image_response = requests.get(profile_pic_url, headers=HEADERS, timeout=10)
                if image_response.status_code == 200:
                    image_path = os.path.join(DOWNLOAD_FOLDER, f"{username}_dp.jpg")
                    with open(image_path, "wb") as f:
                        f.write(image_response.content)
                    image_url = f"/{image_path}"
                else:
                    error = "Failed to download the profile picture."
            except Exception as e:
                error = f"Failed to download the profile picture: {str(e)}"

    return render_template("index.html", image_url=image_url, error=error)

if __name__ == "__main__":
    app.run(debug=True)
