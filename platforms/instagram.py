import sys
import os
import time
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
    Returns:
        caption (str), media_list (List[str])
    """
    try:
        title = sys.argv[1]
        text = sys.argv[2]
        hashtags = sys.argv[3]
        raw = sys.argv[4]
    except IndexError:
        print("Usage: python instagram.py <title> <text> <hashtags> <media_paths>")
        sys.exit(1)

    caption = f"{title}\n\n{text}\n\n{hashtags}"
    media_list = [p.strip() for p in raw.split(";") if p.strip()]
    return caption, media_list

def post_to_instagram(caption, media_list):
    # Reuse your Chrome session to stay logged in
    opts = Options()
    opts.add_argument(f"user-data-dir={os.path.join(os.getcwd(), 'cookies')}")

    driver = webdriver.Chrome(options=opts)
    driver.get("https://www.instagram.com/")
    # wait for the main nav to appear
    WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "nav"))
    )
    time.sleep(2)

    try:
        # 1) Click the New Post icon by SVG aria-label

        
        new_post_svg = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="New post"]'))
        )
        new_post_svg.click()
        
        new_post = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Post"]'))
        )
        new_post.click()

        # 2) Wait for file input & upload up to 10 items
        file_input = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
        )

        valid = []
        for p in media_list:
            if os.path.exists(p):
                valid.append(os.path.abspath(p))
            else:
                print(f"[!] Not found, skipping: {p}")

        if not valid:
            print("[!] No valid media files; Instagram needs at least one.")
            driver.quit()
            return

        if len(valid) > 10:
            print("[!] Limiting to first 10 files (carousel max).")
            valid = valid[:10]

        file_input.send_keys("\n".join(valid))
        print(f"[*] Uploaded {len(valid)} file(s)")
        time.sleep(3)
        
        
        
        select_crop = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Select crop"]'))
        )
        select_crop.click()
        
        crop_portrait_icon = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'svg[aria-label="Crop portrait icon"]'))
        )
        crop_portrait_icon.click()        
        

        # 3) Click Next (Filters)
        nxt = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Next']"))
        )
        nxt.click()
        time.sleep(1)

        # 4) Click Next (Caption)
        nxt = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Next']"))
        )
        nxt.click()
        time.sleep(1)
        

        # 5) Enter caption
        ta = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Write a caption..."]'))
        )
        ta.click()
        ta.clear()
        ta.send_keys(caption)
        time.sleep(1)

        # 6) Share
        share = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//div[text()='Share']"))
        )
        share.click()
        
        shared = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, "//div[@role='heading' and text()='Post shared']"))
        )
        print("[✓] Instagram post shared!")
            
                    

    except Exception as e:
        print(f"[X] Failed to post to Instagram: {e}")
    finally:
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    caption, media = get_post_data()
    post_to_instagram(caption, media)
