# facebook_post.py

import sys
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

def get_post_data():
    """
    Args:
        sys.argv[1]: title
        sys.argv[2]: text
        sys.argv[3]: hashtags
        sys.argv[4]: media_paths (semicolon-separated)
        sys.argv[5]: only_text (True/False)
        sys.argv[6]: only_image (True/False)
        sys.argv[7]: only_video (True/False)
        sys.argv[8]: all_media (True/False)
    Returns:
        dict with caption, media_list, flags
    """
    try:
        title = sys.argv[1]
        text = sys.argv[2]
        hashtags = sys.argv[3]
        raw = sys.argv[4]
        only_text = sys.argv[5].lower() == "true"
        only_image = sys.argv[6].lower() == "true"
        only_video = sys.argv[7].lower() == "true"
        all_media = sys.argv[8].lower() == "true"
    except IndexError:
        print("Usage: python facebook_post.py <text> <hashtags> <media_paths> <only_text> <only_image> <only_video> <all_media>")
        sys.exit(1)

    caption = f"{title}\n\n{text}\n\n{hashtags}".strip()
    media_list = [p.strip() for p in raw.split(";") if p.strip()]

    return {
        "caption": caption,
        "media_list": media_list,
        "only_text": only_text,
        "only_image": only_image,
        "only_video": only_video,
        "all_media": all_media,
    }

def post_to_facebook(data):
    opts = Options()
    opts.add_argument(f"user-data-dir={os.path.join(os.getcwd(), 'cookies')}")

    driver = webdriver.Chrome(options=opts)
    driver.get("https://www.facebook.com/")
    
    try:
        create_post_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Photo/video']"))
        )
        time.sleep(2)

        # 1) Open post dialog
        create_post_btn.click()


        # 2) Handle text
        add_caption = (
            data["only_text"] or 
            (data["only_text"] and (data["only_image"] or data["only_video"])) or
            data["all_media"]
        )

        if add_caption:
            textarea = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[contenteditable='true'][role='textbox']")))
            textarea.click()
            textarea.send_keys(data["caption"])
            time.sleep(1)





        # 3) Handle media
        if not (data["only_text"] and not (data["only_image"] or data["only_video"])):  # Not pure text-only
            file_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
            )

            valid_files = []
            for path in data["media_list"]:
                if os.path.exists(path):
                    valid_files.append(os.path.abspath(path))
                else:
                    print(f"[!] Skipping missing file: {path}")

            if valid_files:
                filtered_files = []

                if data["all_media"]:
                    filtered_files = valid_files
                else:
                    if data["only_image"]:
                        filtered_files += [p for p in valid_files if is_image(p)]
                    if data["only_video"]:
                        filtered_files += [p for p in valid_files if is_video(p)]

                # Remove duplicates if both image + video selected
                filtered_files = list(dict.fromkeys(filtered_files))

                if not filtered_files:
                    print("[!] No valid media to upload after filtering.")
                else:
                    if len(filtered_files) > 20:
                        print("[!] Facebook allows max 10 media files. Trimming.")
                        filtered_files = filtered_files[:20]

                    file_input.send_keys("\n".join(filtered_files))
                    print(f"[*] Uploaded {len(filtered_files)} file(s)")
                    time.sleep(3)
            else:
                print("[!] No valid media found.")

        # 4) Post it
        post_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Post']"))
        )
        post_btn.click()

        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH,"//span[contains(text(),'Your post is being processed')]")))
        print("[✓] Facebook post shared!")
        driver.quit()
        

    except Exception as e:
        print(f"[X] Failed to post to Facebook: {e}")

    finally:
        time.sleep(5)
        driver.quit()

def is_image(path):
    return path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))

def is_video(path):
    return path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv', '.wmv'))

if __name__ == "__main__":
    data = get_post_data()
    post_to_facebook(data)
