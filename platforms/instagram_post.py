import sys
import os
import time
import json
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
        sys.argv[4]: media_paths (semicolon-separated)
        sys.argv[5]: orientation ("Portrait" or "Full Screen" or other)
    Returns:
        caption (str), media_list (List[str]), orientation (str)
    """
    if len(sys.argv) < 5:
        print("Usage: python instagram_post.py <title> <text> <hashtags> <media_paths> [orientation]")
        sys.exit(1)

    title       = sys.argv[1]
    text        = sys.argv[2]
    hashtags    = sys.argv[3]
    raw_media   = sys.argv[4]
    orientation = sys.argv[5] if len(sys.argv) > 5 else ""

    caption = f"{title}\n\n{text}\n\n{hashtags}"
    media_list = [p.strip() for p in raw_media.split(";") if p.strip()]
    return caption, media_list, orientation

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

def post_to_instagram(caption, media_list, orientation):

    driver = webdriver.Chrome(options=opts)
    driver.get("https://www.instagram.com/")
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "nav"))
    )
    time.sleep(2)

    try:
        # 1) Open New Post dialog
        new_post_svg = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="New post"]'))
        )
        new_post_svg.click()
        
        new_post = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Post"]'))
        )
        new_post.click()

        # 2) Upload media
        file_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        )

        valid = []
        allowed_extensions = ('.mp4', '.mov', '.avi', '.mkv', '.webm', '.jpg', '.jpeg', '.png')

        for p in media_list:
            if os.path.exists(p) and p.lower().endswith(allowed_extensions):
                valid.append(os.path.abspath(p))
                if len(valid) == 10:
                    break  # Stop after collecting 10 valid files
            elif not os.path.exists(p):
                print(f"[!] Not found, skipping: {p}")
            else:
                print(f"[!] Unsupported file type, skipping: {p}")

        if not valid:
            print("[!] No valid media files; Instagram needs at least one.")
            driver.quit()
            return



        if valid:
            file_input.send_keys("\n".join(valid))
            print(f"[*] Uploaded: {', '.join(valid)}")
            time.sleep(3)
        else:
            print("[!] No valid media files; Instagram needs at least one.")
            driver.quit()
            return


        # 3) Select crop based on orientation
        select_crop = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Select crop"]'))
        )
        select_crop.click()

        # choose correct crop icon
        icon_selector = None
        if orientation.lower() == "portrait":
            icon_selector = 'svg[aria-label="Crop portrait icon"]'
        elif orientation.lower() in ("full screen", "fullscreen"):
            icon_selector = 'svg[aria-label="Crop landscape icon"]'
        elif orientation.lower() == "square":
            # default to square crop if no/unknown orientation
            icon_selector = 'svg[aria-label="Crop square icon"]'
        else:
            icon_selector = 'svg[aria-label="Crop square icon"]'

        crop_icon = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, icon_selector))
        )
        crop_icon.click()
        print(f"[*] Applied {orientation or 'Square'} crop")
        time.sleep(1)

        # 4) Next → Filters
        nxt = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Next']"))
        )
        nxt.click()
        time.sleep(1)

        # 5) Next → Caption
        nxt = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Next']"))
        )
        nxt.click()
        time.sleep(1)

        # 6) Enter caption
        ta = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Write a caption..."]'))
        )
        ta.click()
        ta.clear()
        ta.send_keys(caption)
        time.sleep(1)

        # 7) Share
        share = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Share']"))
        )
        share.click()
        
        

        

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[@role='heading' and (text()='Post shared' or text()='Reel shared')]"
            ))
        )
        print("[✓] Instagram content shared!")


    except Exception as e:
        print(f"[X] Failed to post to Instagram Post: {e}")
    finally:
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    caption, media, orientation = get_post_data()
    post_to_instagram(caption, media, orientation)
