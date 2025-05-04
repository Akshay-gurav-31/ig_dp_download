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
    if request.method == "POST":
        username = request.form.get("username")
        if username:
            try:
                # Scrape Instagram profile
                url = f"https://www.instagram.com/{username}/"
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = requests.get(url, headers=headers)
                if response.status_code != 200:
                    return render_template("index.html", error="Profile not found or private.")

                # Parse HTML to find the profile picture URL
                soup = BeautifulSoup(response.text, "html.parser")
                meta_tag = soup.find("meta", property="og:image")
                if not meta_tag:
                    return render_template("index.html", error="Could not find profile picture.")

                image_url = meta_tag["content"]

                # Download the image
                image_response = requests.get(image_url, headers=headers)
                if image_response.status_code == 200:
                    image_path = os.path.join(DOWNLOAD_FOLDER, f"{username}_dp.jpg")
                    with open(image_path, "wb") as f:
                        f.write(image_response.content)
                    image_url = f"/{image_path}"  # URL to display in the frontend
                else:
                    return render_template("index.html", error="Failed to download image.")

            except Exception as e:
                return render_template("index.html", error=f"Error: {str(e)}")

    return render_template("index.html", image_url=image_url)

if __name__ == "__main__":
    app.run(debug=True)
