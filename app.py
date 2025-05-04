from flask import Flask, render_template, request
import instaloader
import os
import shutil

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
                # Initialize Instaloader
                L = instaloader.Instaloader()

                # Try to load the profile
                profile = instaloader.Profile.from_username(L.context, username)

                # Check if the profile is private
                if profile.is_private:
                    error = "This account is private. Profile picture cannot be accessed."
                    return render_template("index.html", error=error)

                # Download the profile picture
                L.download_profilepic(profile)

                # The profile picture is saved in a folder named after the username
                # Find the profile picture file (usually a .jpg file)
                profile_folder = username
                for file in os.listdir(profile_folder):
                    if file.endswith(".jpg") or file.endswith(".jpeg"):
                        # Move the file to the downloads folder
                        src_path = os.path.join(profile_folder, file)
                        dest_path = os.path.join(DOWNLOAD_FOLDER, f"{username}_dp.jpg")
                        shutil.move(src_path, dest_path)
                        break
                else:
                    error = "Could not find the profile picture after downloading."
                    return render_template("index.html", error=error)

                # Clean up the profile folder
                shutil.rmtree(profile_folder)

                # Set the image URL for display
                image_url = f"/{dest_path}"

            except instaloader.exceptions.ProfileNotExistsException:
                error = "Profile not found."
                return render_template("index.html", error=error)
            except instaloader.exceptions.PrivateProfileNotFollowedException:
                error = "This account is private. Profile picture cannot be accessed."
                return render_template("index.html", error=error)
            except instaloader.exceptions.ConnectionException:
                error = "Failed to connect to Instagram. You might be rate-limited."
                return render_template("index.html", error=error)
            except Exception as e:
                error = f"An error occurred: {str(e)}"
                return render_template("index.html", error=error)

    return render_template("index.html", image_url=image_url, error=error)

if __name__ == "__main__":
    app.run(debug=True)
