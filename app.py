from flask import Flask, request, jsonify, send_from_directory, render_template
import instaloader
import os
from datetime import datetime
import time

app = Flask(__name__)

def download_instagram_profile(username):
    try:
        L = instaloader.Instaloader(
            download_pictures=True,
            download_videos=False,
            download_video_thumbnails=False,
            download_geotags=False,
            download_comments=False,
            save_metadata=False,
            compress_json=False,
            quiet=True,
            request_timeout=60
        )
        
        # Add login (uncomment and replace YOUR_USERNAME for private accounts)
        # L.load_session_from_file('YOUR_USERNAME')
        
        profile = instaloader.Profile.from_username(L.context, username)
        
        profile_info = {
            "username": profile.username,
            "full_name": profile.full_name,
            "biography": profile.biography,
            "followers": profile.followers,
            "following": profile.followees,
            "post_count": profile.mediacount,
            "is_private": profile.is_private,
            "profile_pic_url": profile.get_profile_pic_url()
        }
        
        folder_name = f"downloads/ig_{username}_{datetime.now().strftime('%Y%m%d')}"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        L.download_profilepic(profile)
        downloads = [{"name": "Profile picture", "status": "success", "path": f"{folder_name}/{profile.username}.jpg"}]
        
        if not profile.is_private:
            posts = profile.get_posts()
            for i, post in enumerate(posts):
                if i >= 12:
                    break
                try:
                    L.download_post(post, target=folder_name)
                    downloads.append({"name": f"Post {i+1}", "status": "success", "path": f"{folder_name}/{post.shortcode}.jpg"})
                    time.sleep(5)
                except Exception as e:
                    downloads.append({"name": f"Post {i+1}", "status": "failed", "error": str(e)})
        
        return {
            "status": "success",
            "profile": profile_info,
            "folder": folder_name,
            "downloads": downloads
        }
    
    except instaloader.exceptions.ProfileNotExistsException:
        return {"status": "error", "message": "Profile doesn't exist or is unavailable"}
    except instaloader.exceptions.PrivateProfileNotFollowedException:
        return {"status": "error", "message": "Private account - login required"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.route('/')
def index():
    return render_template('index.html')  # Serve the HTML page from templates/

@app.route('/download', methods=['POST'])
def download():
    username = request.json.get('username')
    if not username:
        return jsonify({"status": "error", "message": "Username is required"}), 400
    
    result = download_instagram_profile(username)
    return jsonify(result)

@app.route('/download_file/<path:filename>')
def download_file(filename):
    return send_from_directory('downloads', filename, as_attachment=True)

if __name__ == "__main__":
    os.makedirs('downloads', exist_ok=True)

    # Use Render's provided port if available
    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if not specified by Render
    print(f"Starting server on http://0.0.0.0:{port}")
    
    app.run(debug=True, host='0.0.0.0', port=port)
