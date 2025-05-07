import tkinter as tk
from tkinter import messagebox
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DATA_DIR = "data"
PROFILE_FILE = os.path.join(DATA_DIR, "profiles.json")
COOKIES_DIR = "cookies"
ALL_PLATFORMS = ["Facebook", "Instagram", "Twitter", "LinkedIn"]
PLATFORM_URLS = {
    "Facebook": "https://www.facebook.com/",
    "Instagram": "https://www.instagram.com/",
    "Twitter": "https://www.twitter.com/",
    "LinkedIn": "https://www.linkedin.com/"
}

def load_user_profile():
    if not os.path.exists(PROFILE_FILE):
        return None
    with open(PROFILE_FILE, "r") as f:
        return json.load(f)

def save_user_profile(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=4)

def open_platform_session(platform, profile_name):
    try:
        cookies_path = os.path.join(COOKIES_DIR, profile_name.replace(" ", "_"), platform.lower())
        os.makedirs(cookies_path, exist_ok=True)

        options = Options()
        options.add_argument(f"--user-data-dir={cookies_path}")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(options=options)
        driver.get(PLATFORM_URLS[platform])

        messagebox.showinfo("Manage", f"You can now manage your {platform} account.\nClose the browser window when done.")
        driver.quit()

    except Exception as e:
        messagebox.showerror("Error", f"Failed to open {platform} session:\n{str(e)}")

def verify_password(entered_password, saved_password):
    return entered_password == saved_password  # For real-world use, use a hash comparison

def manage_platforms_gui():
    profile = load_user_profile()
    if not profile:
        messagebox.showerror("Error", "No profile found. Please create one first.")
        return

    # Authentication popup
    auth = tk.Tk()
    auth.title("Verify User")
    auth.geometry("300x180")
    auth.configure(bg="#f4f4f4")

    tk.Label(auth, text=f"Welcome {profile['name']}", bg="#f4f4f4", font=("Arial", 11)).pack(pady=10)
    tk.Label(auth, text="Enter Password:", bg="#f4f4f4").pack()
    password_entry = tk.Entry(auth, show="*", width=30)
    password_entry.pack(pady=5)

    def authenticate():
        if verify_password(password_entry.get(), profile['password']):
            auth.destroy()
            launch_platform_manager(profile)
        else:
            messagebox.showerror("Authentication Failed", "Incorrect password.")

    tk.Button(auth, text="Login", command=authenticate, bg="#4CAF50", fg="white", width=15).pack(pady=10)
    auth.mainloop()

def launch_platform_manager(profile):
    profile_name = profile['name']

    window = tk.Tk()
    window.title("Manage Platforms")
    window.geometry("400x400")
    window.configure(bg="#f4f4f4")

    tk.Label(window, text="Manage Your Platforms", bg="#f4f4f4", font=("Arial", 13)).pack(pady=15)

    for platform in ALL_PLATFORMS:
        frame = tk.Frame(window, bg="#f4f4f4")
        frame.pack(pady=8)

        tk.Label(frame, text=platform, bg="#f4f4f4", font=("Arial", 11)).pack(side=tk.LEFT, padx=10)
        tk.Button(frame, text="Manage", bg="#2196F3", fg="white", width=15,
                  command=lambda p=platform: open_platform_session(p, profile_name)).pack(side=tk.LEFT)

    window.mainloop()

# Run the GUI
if __name__ == "__main__":
    manage_platforms_gui()
