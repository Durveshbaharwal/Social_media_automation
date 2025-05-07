import tkinter as tk
import os

import json
import subprocess
from tkinter import messagebox
import gui.manage_platforms
from gui.new_gui_post import PostCreationApp

DATA_DIR = "data"
PROFILE_FILE = os.path.join(DATA_DIR, "profiles.json")


def save_profile(username, password, name):
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    profile_data = {
        "name": name,
        "username": username,
        "password": password
    }

    # Check if the file exists and load existing data
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            try:
                profiles = json.load(f)
            except json.JSONDecodeError:
                profiles = {}  # Initialize empty profiles if file is corrupted

    else:
        profiles = {}

    # Add the new profile to the dictionary, using the username as key
    profiles[username] = profile_data

    # Save updated profiles to the file
    with open(PROFILE_FILE, "w") as f:
        json.dump(profiles, f, indent=4)



def load_existing_profile():
    if not os.path.exists(PROFILE_FILE):
        return None

    with open(PROFILE_FILE, "r") as f:
        try:
            profiles = json.load(f)
        except json.JSONDecodeError:
            return None  # If the JSON is corrupted, return None.

    return profiles  # Return the entire profile dictionary (not just a single profile)






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
        tk.Label(self.window, text=title, bg="#f2f2f2", font=("Arial", 14, "bold")).pack(pady=(10, 10))

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
            if self.password_entry.cget("show") == "*":
                self.password_entry.config(show="")
            else:
                self.password_entry.config(show="*")

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

        if self.mode == "login":
            existing = load_existing_profile(username)
            if not existing:
                messagebox.showerror("Error", "No profile found for this username.")
                return
            if existing["password"] != password:
                messagebox.showerror("Error", "Password incorrect.")
                return
            messagebox.showinfo("Success", "Logged in successfully.")
        else:
            save_profile(username, password, name)
            messagebox.showinfo("Success", "Profile saved successfully.")


        self.window.destroy()
        subprocess.run(["python", "gui/manage_platforms.py"])


class ProfileSelectorApp:
    def __init__(self, root):
        self.window = root
        self.window.title("Select Profile")
        self.window.geometry("400x300")
        self.window.configure(bg="#f9f9f9")

        # Ensure self.profile is a dictionary (loaded profiles)
        self.profile = load_existing_profile()  # This loads the profiles dictionary
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.window, text="Welcome to Social Media Automation", bg="#f9f9f9",
                 font=("Arial", 14, "bold")).pack(pady=(20, 10))

        # If profiles exist, allow login with existing profile
        if self.profile:
            username = list(self.profile.keys())[0]  # Get the first profile username
            use_existing_profile_button = tk.Button(self.window, text=f"Use Existing Profile ({username})", width=30,
                                                     command=self.use_existing_profile, bg="#4CAF50", fg="white")
            use_existing_profile_button.pack(pady=10)
        else:
            use_existing_profile_button = None  # If no profiles exist, don't create the button

        # Disable "Login with Another Profile" button if no profiles
        login_button = tk.Button(self.window, text="Login with Another Profile", width=30,
                                 command=self.login_with_another, bg="#2196F3", fg="white")
        login_button.pack(pady=10)

        if not self.profile:  # If no profile exists, disable the login button
            login_button.config(state="disabled")

        tk.Button(self.window, text="Create New Profile", width=30,
                  command=self.create_new_profile, bg="#9C27B0", fg="white").pack(pady=10)

    def use_existing_profile(self):
        self.window.destroy()
        root = tk.Tk()
        PostCreationApp(root)
        root.mainloop()

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



def main():
    root = tk.Tk()
    ProfileSelectorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
