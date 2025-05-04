from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import re
import os

app = Flask(__name__)

# Folder to save downloaded DPs
DOWNLOAD_FOLDER = "static/downloads"
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route("/", methods=["GET", "POST"])
def index():
    image_url = None
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            try:
                # Use a mobile user agent to fetch the mobile version of the page
                url = f"https://www.instagram.com/{username}/?hl=en"
                headers = {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
                }
                response = requests.get(url, headers=headers, timeout=10)

                # Check if the profile exists
                if response.status_code != 200:
                    error = "Profile not found or inaccessible."
                    return render_template("index.html", error=error)

                # Parse the HTML with BeautifulSoup
                soup = BeautifulSoup(response.text, "html.parser")

                # Check if the profile is private by looking for the "This Account is Private" text
                private_indicator = soup.find(string=re.compile("This Account is Private"))
                if private_indicator:
                    error = "This account is private. Profile picture cannot be accessed."
                    return render_template("index.html", error=error)

                # Try to find the profile picture URL in a <meta> tag (og:image)
                meta_tag = soup.find("meta", property="og:image")
                profile_pic_url = None
                if meta_tag and meta_tag.get("content"):
                    profile_pic_url = meta_tag["content"]
                else:
                    # Fallback: Look for JSON data in a <script> tag
                    script_tags = soup.find_all("script", type="text/javascript")
                    for script in script_tags:
                        if script.string and "profile_pic_url" in script.string:
                            match = re.search(r'"profile_pic_url":"(.*?)"', script.string)
                            if match:
                                profile_pic_url = match.group(1).replace("\\/", "/")
                                break

                if not profile_pic_url:
                    error = "Could not find profile picture. Instagram may have changed its structure."
                    return render_template("index.html", error=error)

                # Download the image
                image_response = requests.get(profile_pic_url, headers=headers, timeout=10)
                if image_response.status_code == 200:
                    image_path = os.path.join(DOWNLOAD_FOLDER, f"{username}_dp.jpg")
                    with open(image_path, "wb") as f:
                        f.write(image_response.content)
                    image_url = f"/{image_path}"  # URL to display in the frontend
                else:
                    error = "Failed to download the profile picture."
                    return render_template("index.html", error=error)

            except requests.exceptions.RequestException as e:
                error = f"Failed to connect to Instagram: {str(e)}"
                return render_template("index.html", error=error)
            except Exception as e:
                error = f"An error occurred: {str(e)}"
                return render_template("index.html", error=error)

    return render_template("index.html", image_url=image_url, error=error)

if __name__ == "__main__":
    app.run(debug=True)
