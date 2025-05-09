import tkinter as tk
import os
import json
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from gui.new_gui_post import PostCreationApp

# Constants
DATA_DIR = "data"
PROFILE_FILE = os.path.join(DATA_DIR, "profiles.json")

# Profile Handling
def save_profile(username, password, name):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    profile_data = {
        "name": name,
        "username": username,
        "password": password
    }

    profiles = load_existing_profiles() or {}
    profiles[username] = profile_data

    with open(PROFILE_FILE, "w") as f:
        json.dump(profiles, f, indent=4)

def load_existing_profiles():
    if not os.path.exists(PROFILE_FILE):
        return None
    with open(PROFILE_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return None

# Platform Management
def load_profile(username):
    profiles = load_existing_profiles()
    return profiles.get(username, {}) if profiles else {}

def launch_browser(platform, username):
    profile = load_profile(username)
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

# GUI Classes
class ProfileSetupApp:
    def __init__(self, root, mode="new"):
        self.window = root
        self.mode = mode
        self.window.title("Profile Setup")
        self.window.geometry("400x350")
        self.window.configure(bg="#f2f2f2")
        self.create_widgets()

    def create_widgets(self):
        title = "Create New Profile" if self.mode == "new" else "Login with Another Profile"
        tk.Label(self.window, text=title, bg="#f2f2f2", font=("Arial", 14, "bold")).pack(pady=10)

        tk.Label(self.window, text="Your Name:", bg="#f2f2f2").pack()
        self.name_entry = tk.Entry(self.window, width=30)
        self.name_entry.pack()

        tk.Label(self.window, text="Username:", bg="#f2f2f2").pack(pady=(10, 0))
        self.username_entry = tk.Entry(self.window, width=30)
        self.username_entry.pack()

        tk.Label(self.window, text="Password:", bg="#f2f2f2").pack(pady=(10, 0))
        self.password_entry = tk.Entry(self.window, show="*", width=30)
        self.password_entry.pack()

        def toggle_password():
            self.password_entry.config(show="" if self.password_entry.cget("show") == "*" else "*")

        tk.Button(self.window, text="Show Password", command=toggle_password, bg="#f2f2f2").pack(pady=(5, 10))

        btn_label = "Save Profile" if self.mode == "new" else "Login"
        tk.Button(self.window, text=btn_label, command=self.save_or_login_profile,
                  bg="#4CAF50", fg="white", width=20).pack(pady=20)

    def save_or_login_profile(self):
        name = self.name_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password or (self.mode == "new" and not name):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        profiles = load_existing_profiles()

        if self.mode == "login":
            if not profiles or username not in profiles:
                messagebox.showerror("Error", "No profile found for this username.")
                return
            if profiles[username]["password"] != password:
                messagebox.showerror("Error", "Password incorrect.")
                return
            messagebox.showinfo("Success", "Logged in successfully.")
        else:
            save_profile(username, password, name)
            messagebox.showinfo("Success", "Profile saved successfully.")

        self.window.destroy()
        launch_platform_gui(username)


class ManagePlatformsApp:
    def __init__(self, root, username):
        self.window = root
        self.username = username
        self.window.title("Manage Platforms")
        self.window.geometry("400x400")
        self.window.configure(bg="#f2f2f2")
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.window, text="Log in to your Platforms", bg="#f2f2f2", font=("Arial", 14)).pack(pady=20)

        platforms = ["Facebook", "Instagram", "LinkedIn", "Twitter"]
        for platform in platforms:
            tk.Button(self.window, text=f"Login to {platform}", width=25,
                      command=lambda p=platform: launch_browser(p, self.username),
                      bg="#4285F4", fg="white").pack(pady=5)

        tk.Button(self.window, text="Save and Exit", width=20, bg="#d9534f", fg="white",
                  command=self.window.quit).pack(pady=(30, 5))

        tk.Button(self.window, text="Save and Start Posting", width=20, bg="#5cb85c", fg="white",
                  command=self.launch_post_gui).pack(pady=5)

    def launch_post_gui(self):
        self.window.destroy()
        root = tk.Tk()
        PostCreationApp(root)
        root.mainloop()


class ProfileSelectorApp:
    def __init__(self, root):
        self.window = root
        self.window.title("Select Profile")
        self.window.geometry("400x300")
        self.window.configure(bg="#f9f9f9")
        self.profile = load_existing_profiles()
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.window, text="Welcome to Social Media Automation", bg="#f9f9f9",
                 font=("Arial", 14, "bold")).pack(pady=(20, 10))

        if self.profile:
            first_username = list(self.profile.keys())[0]
            tk.Button(self.window, text=f"Use Existing Profile ({first_username})", width=30,
                      command=lambda: self.launch_platform_gui(first_username), bg="#4CAF50", fg="white").pack(pady=10)

        login_button = tk.Button(self.window, text="Login with Another Profile", width=30,
                                 command=self.login_with_another, bg="#2196F3", fg="white")
        login_button.pack(pady=10)

        if not self.profile:
            login_button.config(state="disabled")

        tk.Button(self.window, text="Create New Profile", width=30,
                  command=self.create_new_profile, bg="#9C27B0", fg="white").pack(pady=10)

    def login_with_another(self):
        self.window.destroy()
        root = tk.Tk()
        ProfileSetupApp(root, mode="login")
        root.mainloop()

    def create_new_profile(self):
        self.window.destroy()
        root = tk.Tk()
        ProfileSetupApp(root, mode="new")
        root.mainloop()

    def launch_platform_gui(self, username):
        self.window.destroy()
        launch_platform_gui(username)


def launch_platform_gui(username):
    root = tk.Tk()
    ManagePlatformsApp(root, username)
    root.mainloop()


def main():
    root = tk.Tk()
    ProfileSelectorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
