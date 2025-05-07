import sys
import os
import time
import json
import pyautogui
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_post_data():
    """
    Args:
        sys.argv[1]: title
        sys.argv[2]: text
        sys.argv[3]: hashtags
        sys.argv[4]: media_paths
        sys.argv[5:]: linkedin_options (multiple options)

    Returns:
        caption (str), media_list (list), options (list of str)
    """
    if len(sys.argv) < 5:
        print("Usage: python linkedin.py <title> <text> <hashtags> <media_paths> <linkedin_option1> <linkedin_option2> ...")
        sys.exit(1)

    title = sys.argv[1]
    text = sys.argv[2]
    hashtags = sys.argv[3]
    raw_media = sys.argv[4]
    options = sys.argv[5:]  # ["Video Only", "Only Article", "Image Posts"]

    caption = f"{title}\n\n{text}\n\n{hashtags}"
    media_list = [p.strip() for p in raw_media.split(";") if os.path.exists(p.strip())]

    return caption, media_list, options

# Load active profile
PROFILE_FILE = "data/profiles.json"

with open(PROFILE_FILE, "r") as f:
    profile = json.load(f)
    
profile_name = profile.get("name", "").replace(" ", "_")
platform = "Linkedin"  # <-- Update this per script

# Set cookies path
cookies_path = os.path.join(os.getcwd(), "cookies", profile_name, platform.lower())
os.makedirs(cookies_path, exist_ok=True)

# Launch browser with isolated cookies
opts = Options()
opts.add_argument(f"user-data-dir={cookies_path}")
opts.add_argument("--disable-notifications")
opts.add_argument("--start-maximized")

def post_to_linkedin(caption, media_list, option):

    driver = webdriver.Chrome(options=opts)

    driver.get("https://www.linkedin.com/feed/")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.ID, "global-nav"))
    )
    print(f"[*] Logged in - Preparing LinkedIn post for: {option}")

    try:
        start_post_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//strong[text()='Start a post']]"))
        )
        start_post_btn.click()

        post_area = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
        )
        post_area.click()
        post_area.send_keys(caption)
        print("[*] Caption inserted.")

        # Handle "Only Article" option (Post only the caption)
        if option == "only article":
            print(f"[*] Posting article only for option: {option}")
            # After caption is inserted, directly click Post button
            post_btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Post']]"))
            )
            post_btn.click()
            
                        # Wait for the toast message to confirm post was successful
            toast = WebDriverWait(driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, "//p[contains(@class, 'artdeco-toast-item__message')]/span[contains(text(), 'Post successful')]"))
            )
            print(f"[✓] LinkedIn post shared successfully for: {option}")
            
            # Wait before moving on to other operations (e.g., image or video posts)
            time.sleep(3)
            
            
        elif option == "video only":
            # Only process video files for "Video Only"
            allowed_exts = ('.mp4', '.mov', '.avi', '.mkv')
            valid_media = []
            for path in media_list:
                if os.path.exists(path) and path.lower().endswith(allowed_exts):
                    valid_media.append(os.path.abspath(path))
                    if len(valid_media) == 20:
                        break
                elif not os.path.exists(path):
                    print(f"[!] File not found, skipping: {path}")
                else:
                    print(f"[!] Invalid file for 'Video Only', skipping: {path}")

            if valid_media:
                print(f"[*] Valid video media: {valid_media}")
                # Add media to post
                add_media_btn = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label,'Add a')]"))
                )
                add_media_btn.click()
                time.sleep(3)
                pyautogui.press("esc")
                time.sleep(3)

                file_input = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                )
                file_input.send_keys("\n".join(valid_media))
                print(f"[*] Uploaded: {', '.join(valid_media)}")
                time.sleep(3)
            else:
                print(f"[!] No valid video media for option: {option}")
        elif option == "image posts":
            # Process image files for "Image Posts"
            allowed_exts = ('.jpg', '.jpeg', '.png', '.mp4', '.mov', '.avi', '.mkv')
            valid_media = []
            for path in media_list:
                if os.path.exists(path) and path.lower().endswith(allowed_exts):
                    valid_media.append(os.path.abspath(path))
                    if len(valid_media) == 20:
                        break
                elif not os.path.exists(path):
                    print(f"[!] File not found, skipping: {path}")
                else:
                    print(f"[!] Invalid file for '{option}', skipping: {path}")

            if valid_media:
                print(f"[*] Valid media: {valid_media}")
                # Add media to post
                add_media_btn = WebDriverWait(driver, 20).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label,'Add a')]"))
                )
                add_media_btn.click()
                time.sleep(3)
                pyautogui.press("esc")
                time.sleep(3)

                file_input = WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
                )
                file_input.send_keys("\n".join(valid_media))
                print(f"[*] Uploaded: {', '.join(valid_media)}")
                time.sleep(3)
            else:
                print(f"[!] No valid media for option: {option}")
        else:
            print(f"[!] Invalid option: {option}. Skipping LinkedIn post.")
            driver.quit()
            return

        if option != "only article":
            # For options other than "Only Article", proceed with the regular flow
            next_button = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@aria-label, 'Next')]"))
            )
            next_button.click()

            post_area = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
            )
            post_area.click()
            post_area.send_keys(caption)
            print("[*] Caption inserted again after media.")

            post_btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Post']]"))
            )
            post_btn.click()

        # Wait for toast message to confirm post was successful
        toast = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, "//p[contains(@class, 'artdeco-toast-item__message')]/span[contains(text(), 'Post successful')]"))
        )
        print(f"[✓] LinkedIn post shared successfully for: {option}")

    except Exception as e:
        print(f"[X] Failed to post on LinkedIn ({option}): {e}")
    finally:
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    caption, media, options = get_post_data()
    for opt in options:
        post_to_linkedin(caption, media, opt)
