import tkinter as tk
import datetime
from tkinter import messagebox
import json
import os

DATA_DIR = "data"
PROFILE_FILE = os.path.join(DATA_DIR, "profiles.json")
ALL_PLATFORMS = ["Facebook", "Instagram", "Twitter", "LinkedIn"]

def load_user_profile():
    if not os.path.exists(PROFILE_FILE):
        messagebox.showerror("Error", "Profile not found. Please create one first.")
        return None
    with open(PROFILE_FILE, "r") as f:
        return json.load(f)

def save_user_profile(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=4)

def manage_platforms_gui():
    profile = load_user_profile()
    if not profile:
        return

    current_platforms = set(profile.get("platforms", []))

    window = tk.Tk()
    window.title("Manage Platforms")
    window.geometry("400x350")
    window.configure(bg="#f4f4f4")

    tk.Label(window, text="Enable or Disable Platforms", bg="#f4f4f4", font=("Arial", 12)).pack(pady=10)

    platform_vars = {}
    for platform in ALL_PLATFORMS:
        var = tk.BooleanVar(value=platform in current_platforms)
        tk.Checkbutton(window, text=platform, variable=var, bg="#f4f4f4").pack(anchor="w", padx=100)
        platform_vars[platform] = var

    def save_changes():
        updated_platforms = [p for p, v in platform_vars.items() if v.get()]
        if not updated_platforms:
            messagebox.showerror("Error", "You must select at least one platform.")
            return
        profile["platforms"] = updated_platforms
        save_user_profile(profile)
        messagebox.showinfo("Success", "Platform preferences updated successfully.")
        window.destroy()

    tk.Button(window, text="Save Changes", command=save_changes, bg="#2196F3", fg="white", width=20).pack(pady=20)

    window.mainloop()

# For direct testing
if __name__ == "__main__":
    manage_platforms_gui()
