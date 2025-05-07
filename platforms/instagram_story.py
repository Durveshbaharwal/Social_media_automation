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

def get_story_data():
    """
    Args:
        sys.argv[1]: title
        sys.argv[2]: text
        sys.argv[3]: hashtags
        sys.argv[4]: media_paths (semicolon-separated)
        sys.argv[5]: orientation ("Portrait" or "Full Screen" or other)
    Returns:
        caption (str), media_list (List[str]), orientation (str)
    """
    if len(sys.argv) < 5:
        print("Usage: python instagram_post.py <title> <text> <hashtags> <media_paths> [orientation]")
        sys.exit(1)

    raw_media   = sys.argv[4]


    media_list = [p.strip() for p in raw_media.split(";") if p.strip()]
    return media_list


# Load active profile
PROFILE_FILE = "data/profiles.json"

with open(PROFILE_FILE, "r") as f:
    profile = json.load(f)
    
profile_name = profile.get("name", "").replace(" ", "_")
platform = "Instagram"  # <-- Update this per script

# Set cookies path
cookies_path = os.path.join(os.getcwd(), "cookies", profile_name, platform.lower())
os.makedirs(cookies_path, exist_ok=True)

# Launch browser with isolated cookies
opts = Options()
opts.add_argument(f"user-data-dir={cookies_path}")
opts.add_argument("--disable-notifications")
opts.add_argument("--start-maximized")


def upload_story(media_list):
    mobile_emulation = {
        "deviceName": "Pixel 2"
    }
    opts.add_experimental_option("mobileEmulation", mobile_emulation)

    driver = webdriver.Chrome(options=options)
    driver.get("https://www.instagram.com/")

    try:
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "nav"))
        )
        time.sleep(3)

        # Click "+" icon for new story (may appear as camera icon or similar)
        plus_buttons = driver.find_elements(By.CSS_SELECTOR, "svg[aria-label='Plus icon']")
        if not plus_buttons:
            new_post_svg = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Home"]'))
            )
            new_post_svg.click()
            
            new_post = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Story"]'))
            )
            new_post.click()

        if not plus_buttons:
            print("[!] New Story button not found.")
            return

        plus_buttons[0].click()
        

        supported_exts = ('.jpg', '.jpeg', '.png')
        valid = []

        for p in media_list:
            if os.path.exists(p) and p.lower().endswith(supported_exts):
                valid.append(os.path.abspath(p))
                break  # Stop after the first valid image file is found
            elif not os.path.exists(p):
                print(f"[!] Not found, skipping: {p}")
            else:
                print(f"[!] Not a video file, skipping: {p}")

        if not valid:
            print("[!] No valid video file found; Instagram Reels needs at least one video.")
            driver.quit()
            return
        print(valid)
        time.sleep(3)
        pyautogui.write(valid[0], interval=0.02)
        WebDriverWait(driver, 20)
        time.sleep(3)
        pyautogui.press("enter")
        print("[*] File path entered into system dialog")
        time.sleep(3)
        pyautogui.press('f12')         # open DevTools
        time.sleep(1)                  # let it finish opening
        pyautogui.hotkey('ctrl', 'shift', 'm')  # toggle device toolbar
        time.sleep(3)
        # wait for desktop UI to load


        # Click “Share to your story”
        share_button = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'span[aria-label="Add to your story"]'))
        )
        share_button.click()
        
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[@role='alert' and (text()='Your photo was added.')]"
            ))
        )
        print("[✓] Instagram Story shared!")

    except Exception as e:
        print(f"[X] Failed to upload story: {e}")
    finally:
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    media_path = get_story_data()
    upload_story(media_path)
