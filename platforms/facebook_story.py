# facebook_story.py

import sys
import os
import time
from selenium import webdriver
import pyautogui
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
        sys.argv[5]: story_option (Photo Story or Text Story)
    Returns:
        story_text (str), image_path (str or None), story_option (str)
    """
    try:
        title = sys.argv[1]
        text = sys.argv[2]
        hashtags = sys.argv[3]
        raw = sys.argv[4]
        story_option = sys.argv[5]
    except IndexError:
        print("Usage: python facebook_story.py <title> <text> <hashtags> <media_paths> <story_option>")
        sys.exit(1)

    story_text = f"{title}\n\n{text}\n\n{hashtags}"
    media_list = [p.strip() for p in raw.split(";") if p.strip()]

    # Filter only image files
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    images = [os.path.abspath(p) for p in media_list if os.path.splitext(p)[-1].lower() in image_extensions and os.path.exists(p)]

    selected_image = images[0] if images else None
    return story_text, selected_image, story_option

def post_story_to_facebook(story_text, image_path, story_option):
    opts = Options()
    opts.add_argument(f"user-data-dir={os.path.join(os.getcwd(), 'cookies')}")

    driver = webdriver.Chrome(options=opts)
    driver.get("https://www.facebook.com/")

    try:
        # Open the 'Create Story' section
        create_story_btn = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(),'Create story')]"))
        )
        create_story_btn.click()
        time.sleep(2)

        if story_option == "Photo Story":
            if not image_path:
                print("[!] No valid image found for Photo Story.")
                driver.quit()
                return

            # Select Photo Story option
            photo_story_option = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Create a Photo Story')]"))
            )
            photo_story_option.click()

            # Upload the image
            file_input = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[type="file"]'))
            )
                  # open DevTools
            time.sleep(1)    
            file_input.send_keys(image_path)
            pyautogui.press("esc")
            print("[*] Uploaded image for Photo Story.")
            time.sleep(3)

        elif story_option == "Text Story":
            # Select Text Story option
            text_story_option = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(),'Create a Text Story')]"))
            )
            text_story_option.click()

            # Enter story text
            textarea = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="textbox"]'))
            )
            textarea.click()
            textarea.send_keys(story_text)
            print("[*] Entered text for Text Story.")
            time.sleep(2)

        else:
            print(f"[!] Unsupported story option: {story_option}")
            driver.quit()
            return

        # Publish the story
        share_btn = WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH,"//span[text()='Share to Story']")))
        share_btn.click()
        print("[✓] Facebook Story shared!")

    except Exception as e:
        print(f"[X] Failed to post Facebook Story: {e}")
    finally:
        time.sleep(5)
        driver.quit()

if __name__ == "__main__":
    story_text, image_path, story_option = get_story_data()
    post_story_to_facebook(story_text, image_path, story_option)
