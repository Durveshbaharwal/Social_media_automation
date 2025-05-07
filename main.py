import os
import datetime
import tkinter as tk
from gui.profile_setup_gui import ProfileSetupApp
from gui.new_gui_post import PostCreationApp

PROFILE_FILE = "data/profiles.json"

def main():
    root = tk.Tk()

    if not os.path.exists(PROFILE_FILE):
        print("Profile not found. Launching profile setup...")
        app = ProfileSetupApp(root)
    else:
        print("Profile found. Launching post creation...")
        app = PostCreationApp(root)

    root.mainloop()

if __name__ == "__main__":
    main()




