import tkinter as tk
import datetime
from tkinter import messagebox
import json
import os

DATA_DIR = "data"
PROFILE_FILE = os.path.join(DATA_DIR, "profiles.json")

def save_profile(username, password, platforms, name):
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

class ProfileSetupApp:
    def __init__(self, root):
        self.window = root
        self.window.title("Create Your Automation Profile")
        self.window.geometry("400x400")
        self.window.configure(bg="#f2f2f2")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.window, text="Your Name:", bg="#f2f2f2").pack(pady=(10, 0))
        self.name_entry = tk.Entry(self.window, width=30)
        self.name_entry.pack()

        tk.Label(self.window, text="Login ID (Email/Username):", bg="#f2f2f2").pack(pady=(10, 0))
        self.username_entry = tk.Entry(self.window, width=30)
        self.username_entry.pack()

        tk.Label(self.window, text="Password:", bg="#f2f2f2").pack(pady=(10, 0))
        self.password_entry = tk.Entry(self.window, show="*", width=30)
        self.password_entry.pack()

        # Password visibility toggle
        def toggle_password():
            if self.password_entry.cget('show') == "*":
                self.password_entry.config(show="")
            else:
                self.password_entry.config(show="*")

        toggle_button = tk.Button(self.window, text="Show Password", command=toggle_password, bg="#f2f2f2")
        toggle_button.pack(pady=(5, 10))

        tk.Label(self.window, text="Select Platforms to Automate:", bg="#f2f2f2").pack(pady=(15, 5))

        platforms = ["Facebook", "Instagram", "Twitter", "LinkedIn"]
        self.platform_vars = {platform: tk.BooleanVar() for platform in platforms}

        for platform, var in self.platform_vars.items():
            tk.Checkbutton(self.window, text=platform, variable=var, bg="#f2f2f2").pack(anchor='w', padx=100)

        save_button = tk.Button(self.window, text="Save Profile", command=self.save_profile, bg="#4CAF50", fg="white", width=20)
        save_button.pack(pady=20)

    def save_profile(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        name = self.name_entry.get().strip()
        selected_platforms = [platform for platform, var in self.platform_vars.items() if var.get()]

        if not username or not password or not selected_platforms or not name:
            messagebox.showerror("Error", "Please fill in all fields and select at least one platform.")
            return

        save_profile(username, password, selected_platforms, name)
        messagebox.showinfo("Success", "Profile created and saved successfully.")
        self.window.quit()

# To run the application:
if __name__ == "__main__":
    root = tk.Tk()
    app = ProfileSetupApp(root)
    root.mainloop()
