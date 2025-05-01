import instaloader
import time
import os
from datetime import datetime

def download_instagram_profile(username):
    try:
        # Create instance with better configuration
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
        
        # Optional login (uncomment these 3 lines if needed)
        # L.load_session_from_file('YOUR_USERNAME')
        # OR
        # L.interactive_login('YOUR_USERNAME')  # Will prompt for password
        
        try:
            print(f"\nAttempting to download profile: @{username}")
            
            # Get profile
            profile = instaloader.Profile.from_username(L.context, username)
            
            print(f"\nProfile Info:")
            print(f"Username: @{profile.username}")
            print(f"Name: {profile.full_name}")
            print(f"Bio: {profile.biography}")
            print(f"Followers: {profile.followers}")
            print(f"Following: {profile.followees}")
            print(f"Private: {'Yes' if profile.is_private else 'No'}")
            
            # Create download folder
            folder_name = f"ig_{username}_{datetime.now().strftime('%Y%m%d')}"
            if not os.path.exists(folder_name):
                os.makedirs(folder_name)
            
            # FIXED: Profile picture download
            print("\nDownloading profile picture...")
            L.download_profilepic(profile)  # Now with correct arguments
            
            # For public accounts, download posts
            if not profile.is_private:
                print("\nDownloading recent posts (max 12)...")
                posts = profile.get_posts()
                for i, post in enumerate(posts):
                    if i >= 12:  # Limit to 12 posts
                        break
                    try:
                        L.download_post(post, target=folder_name)
                        time.sleep(5)  # Increased delay to avoid blocks
                    except Exception as e:
                        print(f"Couldn't download post {i+1}: {str(e)}")
                        continue
            
            print(f"\n✅ Download complete! Saved in folder: {folder_name}")
            
        except instaloader.exceptions.ProfileNotExistsException:
            print(f"\n❌ Error: @{username} doesn't exist or is unavailable")
        except instaloader.exceptions.PrivateProfileNotFollowedException:
            print(f"\n❌ Error: @{username} is private. You need to follow this account.")
        except Exception as e:
            print(f"\n⚠️ An error occurred: {str(e)}")
            
    except KeyboardInterrupt:
        print("\n⚠️ Download interrupted by user")
    except Exception as e:
        print(f"\n⚠️ Critical error: {str(e)}")

if __name__ == "__main__":
    print("Instagram Profile Downloader v3 (Fixed)")
    print("--------------------------------------")
    print("Note: For private accounts, you need to be logged in")
    username = input("Enter Instagram username (without @): ").strip()
    
    if username:
        download_instagram_profile(username)
    else:
        print("Please enter a valid username")
