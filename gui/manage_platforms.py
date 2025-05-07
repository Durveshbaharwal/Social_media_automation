import tkinter as tk
import os
import json
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import subprocess

# Constants
PROFILE_FILE = "data/profiles.json"

def load_profile():
    with open(PROFILE_FILE, "r") as f:
        return json.load(f)

def launch_browser(platform):
    profile = load_profile()
    profile_name = profile.get("name", "").replace(" ", "_")
    cookies_path = os.path.join(os.getcwd(), "cookies", profile_name, platform.lower())
    os.makedirs(cookies_path, exist_ok=True)

    opts = Options()
    opts.add_argument(f"user-data-dir={cookies_path}")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--start-maximized")

    driver = webdriver.Chrome(options=opts)

    login_urls = {
        "Facebook": "https://www.facebook.com/",
        "Instagram": "https://www.instagram.com/accounts/login/",
        "LinkedIn": "https://www.linkedin.com/login",
        "Twitter": "https://twitter.com/i/flow/login"
    }

    driver.get(login_urls[platform])

class ManagePlatformsApp:
    def __init__(self, root):
        self.window = root
        self.window.title("Manage Platforms")
        self.window.geometry("400x400")
        self.window.configure(bg="#f2f2f2")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.window, text="Log in to your Platforms", bg="#f2f2f2", font=("Arial", 14)).pack(pady=20)

        platforms = ["Facebook", "Instagram", "LinkedIn", "Twitter"]
        for platform in platforms:
            btn = tk.Button(self.window, text=f"Login to {platform}", width=25,
                            command=lambda p=platform: launch_browser(p), bg="#4285F4", fg="white")
            btn.pack(pady=5)

        # Footer buttons
        tk.Button(self.window, text="Save and Exit", width=20, bg="#d9534f", fg="white",
                  command=self.window.quit).pack(pady=(30, 5))

        tk.Button(self.window, text="Save and Start Posting", width=20, bg="#5cb85c", fg="white",
                  command=self.launch_post_gui).pack(pady=5)

    def launch_post_gui(self):
        self.window.destroy()
        subprocess.run(["python", "gui/new_gui_post.py"])  # Replace with actual path if needed

# Run this GUI independently for testing
if __name__ == "__main__":
    root = tk.Tk()
    app = ManagePlatformsApp(root)
    root.mainloop()
