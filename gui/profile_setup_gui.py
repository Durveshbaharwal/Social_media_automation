import tkinter as tk
from tkinter import messagebox
import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DATA_DIR = "data"
PROFILE_FILE = os.path.join(DATA_DIR, "profiles.json")

PLATFORM_URLS = {
    "Facebook": "https://www.facebook.com/",
    "Instagram": "https://www.instagram.com/",
    "Twitter": "https://www.twitter.com/",
    "LinkedIn": "https://www.linkedin.com/"
}


def save_profile_data(username, password, platforms, name):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    profile_data = {
        "name": name,
        "username": username,
        "password": password,
        "platforms": platforms
    }

    with open(PROFILE_FILE, "w") as f:
        json.dump(profile_data, f, indent=4)


def load_profile_data():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    return None


class ProfileSetupApp:
    def __init__(self, root):
        self.window = root
        self.window.title("Profile Setup")
        self.window.geometry("500x500")
        self.window.configure(bg="#f2f2f2")

        self.logged_in_platforms = set()
        self.platform_vars = {}
        self.login_buttons = {}

        self.show_initial_choice()

    def show_initial_choice(self):
        for widget in self.window.winfo_children():
            widget.destroy()

        tk.Label(self.window, text="Welcome to the Automation App", font=("Arial", 14), bg="#f2f2f2").pack(pady=30)

        tk.Button(self.window, text="Login to Existing Profile", width=30, command=self.show_login_screen).pack(pady=10)
        tk.Button(self.window, text="Create New Profile", width=30, command=self.show_profile_creation).pack(pady=10)

    def show_login_screen(self):
        for widget in self.window.winfo_children():
            widget.destroy()

        tk.Label(self.window, text="Login", font=("Arial", 14), bg="#f2f2f2").pack(pady=20)

        tk.Label(self.window, text="Username:", bg="#f2f2f2").pack()
        self.login_username_entry = tk.Entry(self.window, width=30)
        self.login_username_entry.pack()

        tk.Label(self.window, text="Password:", bg="#f2f2f2").pack()
        self.login_password_entry = tk.Entry(self.window, show="*", width=30)
        self.login_password_entry.pack()

        tk.Button(self.window, text="Login", command=self.authenticate_user, bg="#4CAF50", fg="white").pack(pady=15)
        tk.Button(self.window, text="Back", command=self.show_initial_choice).pack()

    def authenticate_user(self):
        entered_username = self.login_username_entry.get().strip()
        entered_password = self.login_password_entry.get().strip()

        data = load_profile_data()
        if data and data["username"] == entered_username and data["password"] == entered_password:
            messagebox.showinfo("Login Successful", f"Welcome back, {data['name']}!")
            self.window.quit()  # You may also redirect to PostCreationApp
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def show_profile_creation(self):
        for widget in self.window.winfo_children():
            widget.destroy()

        tk.Label(self.window, text="Your Name:", bg="#f2f2f2").pack(pady=(10, 0))
        self.name_entry = tk.Entry(self.window, width=30)
        self.name_entry.pack()

        tk.Label(self.window, text="Login ID (Email/Username):", bg="#f2f2f2").pack(pady=(10, 0))
        self.username_entry = tk.Entry(self.window, width=30)
        self.username_entry.pack()

        tk.Label(self.window, text="Password:", bg="#f2f2f2").pack(pady=(10, 0))
        self.password_entry = tk.Entry(self.window, show="*", width=30)
        self.password_entry.pack()

        toggle_button = tk.Button(self.window, text="Show Password", command=self.toggle_password, bg="#f2f2f2")
        toggle_button.pack(pady=(5, 10))

        tk.Label(self.window, text="Select Platforms to Automate and Login:", bg="#f2f2f2").pack(pady=(15, 5))

        self.platform_vars = {}
        self.login_buttons = {}

        for platform in PLATFORM_URLS:
            frame = tk.Frame(self.window, bg="#f2f2f2")
            frame.pack(pady=2)

            var = tk.BooleanVar()
            self.platform_vars[platform] = var

            cb = tk.Checkbutton(frame, text=platform, variable=var, bg="#f2f2f2", command=self.update_save_button_state)
            cb.pack(side=tk.LEFT, padx=10)

            login_btn = tk.Button(frame, text="Login", command=lambda p=platform: self.login_to_platform(p))
            login_btn.pack(side=tk.LEFT)
            self.login_buttons[platform] = login_btn

        self.save_button = tk.Button(self.window, text="Save Profile", command=self.save_profile,
                                     bg="#4CAF50", fg="white", width=20, state=tk.DISABLED)
        self.save_button.pack(pady=20)

        tk.Button(self.window, text="Back", command=self.show_initial_choice).pack()

    def toggle_password(self):
        if self.password_entry.cget('show') == "*":
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

    def login_to_platform(self, platform):
        try:
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Please enter your name before logging in.")
                return

            # Use profile name to isolate cookies
            cookies_dir = os.path.join(os.getcwd(), 'cookies', name.replace(" ", "_"), platform.lower())
            os.makedirs(cookies_dir, exist_ok=True)

            opts = Options()
            opts.add_argument(f"user-data-dir={cookies_dir}")
            opts.add_argument("--disable-notifications")
            opts.add_argument("--start-maximized")

            driver = webdriver.Chrome(options=opts)
            driver.get(PLATFORM_URLS[platform])

            messagebox.showinfo("Login", f"Please log into {platform} in the opened browser.\nClose the browser when done.")
            driver.quit()

            self.logged_in_platforms.add(platform)
            self.update_save_button_state()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open browser for {platform}: {e}")


    def update_save_button_state(self):
        selected = [p for p, var in self.platform_vars.items() if var.get()]
        if selected and all(p in self.logged_in_platforms for p in selected):
            self.save_button.config(state=tk.NORMAL)
        else:
            self.save_button.config(state=tk.DISABLED)

    def save_profile(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        name = self.name_entry.get().strip()
        selected_platforms = [platform for platform, var in self.platform_vars.items() if var.get()]

        if not username or not password or not name or not selected_platforms:
            messagebox.showerror("Error", "Please fill in all fields and select platforms.")
            return

        if not all(platform in self.logged_in_platforms for platform in selected_platforms):
            messagebox.showerror("Error", "You must log into all selected platforms.")
            return

        save_profile_data(username, password, selected_platforms, name)
        messagebox.showinfo("Success", "Profile created and saved successfully.")
        self.window.quit()


# To run standalone
if __name__ == "__main__":
    root = tk.Tk()
    app = ProfileSetupApp(root)
    root.mainloop()
