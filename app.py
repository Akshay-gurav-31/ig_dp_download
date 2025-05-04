from flask import Flask, render_template, request
import requests
import re
import json
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
                # Scrape Instagram profile with a mobile user agent
                url = f"https://www.instagram.com/{username}/"
                headers = {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
                }
                response = requests.get(url, headers=headers)
                
                # Check if the profile exists
                if response.status_code != 200:
                    error = "Profile not found or inaccessible."
                    return render_template("index.html", error=error)

                # Look for JSON data in <script> tags
                script_pattern = re.compile(r'window\._sharedData\s*=\s*({.*?});', re.DOTALL)
                match = script_pattern.search(response.text)
                if not match:
                    error = "Could not find profile data. Instagram may have changed its structure."
                    return render_template("index.html", error=error)

                # Parse the JSON data
                json_data = json.loads(match.group(1))
                user_data = json_data.get("entry_data", {}).get("ProfilePage", [{}])[0].get("graphql", {}).get("user", {})

                # Check if the profile is private
                if user_data.get("is_private"):
                    error = "This account is private. Profile picture cannot be accessed."
                    return render_template("index.html", error=error)

                # Get the profile picture URL
                profile_pic_url = user_data.get("profile_pic_url_hd") or user_data.get("profile_pic_url")
                if not profile_pic_url:
                    error = "Could not find profile picture."
                    return render_template("index.html", error=error)

                # Download the image
                image_response = requests.get(profile_pic_url, headers=headers)
                if image_response.status_code == 200:
                    image_path = os.path.join(DOWNLOAD_FOLDER, f"{username}_dp.jpg")
                    with open(image_path, "wb") as f:
                        f.write(image_response.content)
                    image_url = f"/{image_path}"  # URL to display in the frontend
                else:
                    error = "Failed to download the profile picture."
                    return render_template("index.html", error=error)

            except Exception as e:
                error = f"An error occurred: {str(e)}"
                return render_template("index.html", error=error)

    return render_template("index.html", image_url=image_url, error=error)

if __name__ == "__main__":
    app.run(debug=True)
