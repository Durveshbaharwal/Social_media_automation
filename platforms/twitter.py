import sys
import os
import time
import json
import mimetypes
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_post_data():
    try:
        title = sys.argv[1]
        text = sys.argv[2]
        hashtags = sys.argv[3]
        media_path = sys.argv[4]
        only_text = sys.argv[5].lower() == 'true'
        only_videos = sys.argv[6].lower() == 'true'
        only_images = sys.argv[7].lower() == 'true'
        all_media = sys.argv[8].lower() == 'true'

        # Build caption if only_text or any combo that includes it
        caption = f"{title}\n\n{text}\n\n{hashtags}" if only_text or all_media else ""
        return caption, media_path, only_text, only_videos, only_images, all_media
    except IndexError:
        print("Usage: python twitter.py <title> <text> <hashtags> <media_path> <Only Text> <Only Videos> <Only Images> <All>")
        sys.exit(1)
        
# Load active profile
PROFILE_FILE = "data/profiles.json"

with open(PROFILE_FILE, "r") as f:
    profile = json.load(f)
    
profile_name = profile.get("name", "").replace(" ", "_")
platform = "Facebook"  # <-- Update this per script

# Set cookies path
cookies_path = os.path.join(os.getcwd(), "cookies", profile_name, platform.lower())
os.makedirs(cookies_path, exist_ok=True)

# Launch browser with isolated cookies
opts = Options()
opts.add_argument(f"user-data-dir={cookies_path}")
opts.add_argument("--disable-notifications")
opts.add_argument("--start-maximized")

def post_to_twitter(caption, media_path, only_text, only_videos, only_images, all_media):


    driver = webdriver.Chrome(options=opts)
    driver.get("https://twitter.com/home")
    time.sleep(5)

    driver.execute_script("window.alert = function() {}; window.confirm = function(){ return true; };")

    try:
        tweet_box = driver.find_element(By.CSS_SELECTOR, 'div[data-testid="tweetTextarea_0"]')
        tweet_box.click()
        if caption:
            tweet_box.send_keys(f"{caption}\n")

        # Determine if media should be posted
        include_media = any([only_videos, only_images, all_media])
        if include_media and media_path:
            media_paths = [path.strip() for path in media_path.split(";") if path.strip()]
            valid_media = []

            for path in media_paths:
                if not os.path.exists(path):
                    print(f"[!] File not found: {path}")
                    continue

                mime_type, _ = mimetypes.guess_type(path)
                if not mime_type:
                    print(f"[!] Unknown type: {path}")
                    continue

                is_video = mime_type.startswith("video")
                is_image = mime_type.startswith("image")

                if all_media:
                    valid_media.append(path)
                elif only_videos and is_video:
                    valid_media.append(path)
                elif only_images and is_image:
                    valid_media.append(path)
                elif only_videos and only_images:
                    if is_video or is_image:
                        valid_media.append(path)

                if len(valid_media) >= 4:
                    break  # Twitter limit

            print(f"[*] Uploading {len(valid_media)} media file(s)...")
            for path in valid_media:
                file_input = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                )
                file_input.send_keys(os.path.abspath(path))
                time.sleep(5)

        post_button = WebDriverWait(driver, 20).until(  
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="tweetButtonInline"]')))
        post_button.click()
        print("✅ Tweet sent!")
        
        view_span = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='View']")))
        # Optional: detect if any alerts pop up
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            alert = driver.switch_to.alert
            print(f"[!] Alert: {alert.text}")
            alert.accept()
        except:
            pass
    except Exception as e:
        print(f"[X] Something went wrong: {e}")

    time.sleep(1)
    driver.quit()

if __name__ == "__main__":
    caption, media, only_text, only_videos, only_images, all_media = get_post_data()
    post_to_twitter(caption, media, only_text, only_videos, only_images, all_media)
