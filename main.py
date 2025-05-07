import os
import json
import tkinter as tk
from gui.manage_platforms_gui import manage_platforms_gui
from gui.profile_setup_gui import ProfileSetupApp
from gui.new_gui_post import PostCreationApp

PROFILE_FILE = "data/profiles.json"

def launch_post_creation():
    post_window = tk.Tk()
    PostCreationApp(post_window)
    post_window.mainloop()

def launch_profile_setup():
    profile_window = tk.Tk()
    ProfileSetupApp(profile_window)
    profile_window.mainloop()

def ask_continue_with_existing_profile(username, root):
    prompt_window = tk.Toplevel(root)
    prompt_window.title("Profile Detected")
    prompt_window.geometry("400x200")
    prompt_window.configure(bg="#f2f2f2")

    tk.Label(prompt_window, text=f"Welcome back, {username}!", bg="#f2f2f2", font=("Arial", 12)).pack(pady=(30, 10))
    tk.Label(prompt_window, text="Do you want to continue with the existing profile?", bg="#f2f2f2").pack(pady=(0, 20))

    btn_frame = tk.Frame(prompt_window, bg="#f2f2f2")
    btn_frame.pack()

    def continue_with_profile():
        prompt_window.destroy()
        launch_post_creation()

    def login_with_different():
        prompt_window.destroy()
        launch_profile_setup()

    tk.Button(btn_frame, text="Continue", command=continue_with_profile, width=20, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=10)
    tk.Button(btn_frame, text="Login with Different Account", command=login_with_different, width=25, bg="#f44336", fg="white").pack(side=tk.LEFT, padx=10)

    # Optional Manage Profile Button
    tk.Button(prompt_window, text="Manage Profile", command=manage_platforms_gui, bg="#FF9800", fg="white", width=20).pack(pady=10)

    prompt_window.mainloop()

def main():
    if os.path.exists(PROFILE_FILE):
        try:
            with open(PROFILE_FILE, "r") as f:
                data = json.load(f)
                username = data.get("username", "Unknown User")
                root = tk.Tk()
                root.withdraw()  # Hide the unused root window
                ask_continue_with_existing_profile(username, root)
        except Exception as e:
            print(f"Error reading profile: {e}")
            launch_profile_setup()
    else:
        print("No profile found. Launching profile setup...")
        launch_profile_setup()

    root.mainloop()

if __name__ == "__main__":
    main()
