import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import datetime
from utils.scheduler import schedule_post_with_repeat
from dispatcher.post_dispatcher import dispatch_post
from utils.logger import log_post
import json

class PostCreationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Create New Post")
        self.root.geometry("700x800")

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        # --- Basic Fields ---
        self.title_label = tk.Label(root, text="Post Title:")
        self.title_entry = tk.Entry(root)
        self.text_label = tk.Label(root, text="Post Text:")
        self.text_entry = tk.Text(root, height=5)
        self.hashtags_label = tk.Label(root, text="Hashtags:")
        self.hashtags_entry = tk.Entry(root)

        self.media_type_label = tk.Label(root, text="Media Type:")
        self.media_type_var = tk.StringVar(value="None")
        self.media_types = ["None", "Image", "Video", "All"]
        self.media_type_menu = ttk.Combobox(root, textvariable=self.media_type_var,
                                            values=self.media_types, state="readonly")
        self.media_type_menu.bind("<<ComboboxSelected>>", lambda e: self.toggle_media_fields())

        self.image_path_label = tk.Label(root, text="Select Images:")
        self.image_path_var = tk.StringVar()
        self.image_path_entry = tk.Entry(root, textvariable=self.image_path_var)
        self.image_browse = tk.Button(root, text="Browse Images", command=self.browse_images)

        self.video_path_label = tk.Label(root, text="Select Videos:")
        self.video_path_var = tk.StringVar()
        self.video_path_entry = tk.Entry(root, textvariable=self.video_path_var)
        self.video_browse = tk.Button(root, text="Browse Videos", command=self.browse_videos)

        # --- Platforms ---
        self.platforms_label = tk.Label(root, text="Select Platforms:")
        self.platforms = {
            "Facebook": tk.BooleanVar(),
            "Instagram": tk.BooleanVar(),
            "Twitter": tk.BooleanVar(),
            "LinkedIn": tk.BooleanVar()
        }

        
        
        # --- Facebook Options ---
        self.facebook_story_var = tk.BooleanVar()
        self.facebook_post_var = tk.BooleanVar()


        self.facebook_story_var_choice = tk.StringVar(value="")  # nothing selected by default


        self.facebook_post_options_vars = {
            "Only Text": tk.BooleanVar(),
            "Only Image": tk.BooleanVar(),
            "Only Video": tk.BooleanVar(),
            "All": tk.BooleanVar()
        }

        self.facebook_frame = tk.LabelFrame(root, text="Facebook Options")

        # Story/Post checkboxes
        tk.Checkbutton(self.facebook_frame, text="Facebook Story", variable=self.facebook_story_var, command=self.update_facebook_story_post_options).pack(anchor="w", padx=10)
        tk.Checkbutton(self.facebook_frame, text="Facebook Post", variable=self.facebook_post_var, command=self.update_facebook_story_post_options).pack(anchor="w", padx=10)

        # Story sub-options
        self.facebook_story_frame = tk.LabelFrame(self.facebook_frame, text="Story Options")
        tk.Radiobutton(self.facebook_story_frame, text="Text Story", variable=self.facebook_story_var_choice, value="Text Story").pack(anchor="w", padx=20)
        tk.Radiobutton(self.facebook_story_frame, text="Photo Story", variable=self.facebook_story_var_choice, value="Photo Story").pack(anchor="w", padx=20)


        # Post sub-options
        self.facebook_post_frame = tk.LabelFrame(self.facebook_frame, text="Post Options")
        for name, var in self.facebook_post_options_vars.items():
            tk.Checkbutton(self.facebook_post_frame, text=name, variable=var, command=self.facebook_post_all_override).pack(anchor="w", padx=20)

        self.facebook_frame.grid(row=8, column=0, sticky="w", padx=10)
        self.facebook_frame.grid_remove()  # hidden by default

        
        # Instagram Options Frame
        self.instagram_frame = tk.LabelFrame(root, text="Instagram Options")
        self.instagram_frame.grid(row=8, column=1, sticky="w", padx=10, pady=5)
        self.instagram_frame.grid_remove()

        # Instagram Option Variables
        self.instagram_options_vars = {
            "Post": tk.BooleanVar(),
            "Reel": tk.BooleanVar(),
            "Story": tk.BooleanVar()
        }

        # Checkbuttons for Post, Reel, Story
        for idx, (name, var) in enumerate(self.instagram_options_vars.items()):
            chk = tk.Checkbutton(self.instagram_frame, text=name, variable=var, command=self.update_instagram_orientation)
            chk.grid(row=idx, column=0, sticky="w", padx=10, pady=2)

        # Instagram Orientation Frames inside Instagram Frame
        self.instagram_post_orientation = tk.StringVar()
        self.instagram_reel_orientation = tk.StringVar()

        # Post Orientation Sub-Frame
        self.post_orient_frame = tk.LabelFrame(self.instagram_frame, text="Post Orientation")
        self.post_orient_frame.grid(row=0, column=1, rowspan=2, padx=10, sticky="nw")
        for idx, val in enumerate(["Square", "Landscape", "Portrait"]):
            tk.Radiobutton(self.post_orient_frame, text=val, variable=self.instagram_post_orientation, value=val).grid(row=idx, column=0, sticky="w", padx=5, pady=2)
        self.post_orient_frame.grid_remove()

        # Reel Orientation Sub-Frame
        self.reel_orient_frame = tk.LabelFrame(self.instagram_frame, text="Reel Orientation")
        self.reel_orient_frame.grid(row=2, column=1, rowspan=2, padx=10, sticky="nw")
        for idx, val in enumerate(["Square", "Landscape", "Portrait"]):
            tk.Radiobutton(self.reel_orient_frame, text=val, variable=self.instagram_reel_orientation, value=val).grid(row=idx, column=0, sticky="w", padx=5, pady=2)
        self.reel_orient_frame.grid_remove()

        
        
        # --- Twitter Options ---
        self.twitter_frame = tk.LabelFrame(root, text="Twitter Options")
        self.twitter_frame.grid(row=8, column=2, sticky="w", padx=10, pady=5)
        self.twitter_frame.grid_remove()

        self.twitter_options_vars = {
            "Only Text": tk.BooleanVar(),
            "Only Videos": tk.BooleanVar(),
            "Only Images": tk.BooleanVar(),
            "All": tk.BooleanVar()
        }

        for idx, (name, var) in enumerate(self.twitter_options_vars.items()):
            chk = tk.Checkbutton(self.twitter_frame, text=name, variable=var)
            chk.grid(row=idx, column=0, sticky="w", padx=10, pady=2)

        # --- LinkedIn Options ---
        self.linkedin_frame = tk.LabelFrame(root, text="LinkedIn Options")
        self.linkedin_frame.grid(row=8, column=3, sticky="w", padx=10, pady=5)
        self.linkedin_frame.grid_remove()

        self.linkedin_options_vars = tk.StringVar()

        linkedin_options = ["Video Only", "Only Article", "Image Posts"]
        for idx, val in enumerate(linkedin_options):
            tk.Radiobutton(self.linkedin_frame, text=val, variable=self.linkedin_options_vars, value=val).grid(row=idx, column=0, sticky="w", padx=10, pady=2)






        # --- Scheduling ---
        self.schedule_var = tk.BooleanVar()
        self.schedule_check = tk.Checkbutton(root, text="Schedule Post", variable=self.schedule_var, command=self.toggle_schedule)
        self.schedule_time_label = tk.Label(root, text="Schedule Time (YYYY-MM-DD HH:MM):")
        self.schedule_time_entry = tk.Entry(root)
        self.frequency_label = tk.Label(root, text="Repeat Frequency:")
        self.frequency_var = tk.StringVar(value="None")
        self.frequency_menu = ttk.Combobox(root, textvariable=self.frequency_var, values=["None", "Daily", "Weekly"], state="readonly")

        # --- Post Button ---
        self.post_button = tk.Button(root, text="Post", command=self.create_post)

        self.layout_widgets()
        self.toggle_media_fields()
        self.toggle_schedule()
        self.update_platform_options()

    def layout_widgets(self):
        pad_x, pad_y = 10, 6

        self.title_label.grid(row=0, column=0, padx=pad_x, pady=pad_y, sticky="w")
        self.title_entry.grid(row=0, column=1, columnspan=2, padx=pad_x, pady=pad_y, sticky="we")
        self.text_label.grid(row=1, column=0, padx=pad_x, pady=pad_y, sticky="nw")
        self.text_entry.grid(row=1, column=1, columnspan=2, padx=pad_x, pady=pad_y, sticky="we")
        self.hashtags_label.grid(row=2, column=0, padx=pad_x, pady=pad_y, sticky="w")
        self.hashtags_entry.grid(row=2, column=1, columnspan=2, padx=pad_x, pady=pad_y, sticky="we")

        self.media_type_label.grid(row=3, column=0, padx=pad_x, pady=pad_y, sticky="w")
        self.media_type_menu.grid(row=3, column=1, columnspan=2, padx=pad_x, pady=pad_y, sticky="we")
        self.image_path_label.grid(row=4, column=0, padx=pad_x, pady=pad_y, sticky="w")
        self.image_path_entry.grid(row=4, column=1, padx=pad_x, pady=pad_y, sticky="we")
        self.image_browse.grid(row=4, column=2, padx=pad_x, pady=pad_y)
        self.video_path_label.grid(row=5, column=0, padx=pad_x, pady=pad_y, sticky="w")
        self.video_path_entry.grid(row=5, column=1, padx=pad_x, pady=pad_y, sticky="we")
        self.video_browse.grid(row=5, column=2, padx=pad_x, pady=pad_y)

        self.platforms_label.grid(row=6, column=0, padx=pad_x, pady=pad_y, sticky="w")
        for idx, (name, var) in enumerate(self.platforms.items()):
            chk = tk.Checkbutton(self.root, text=name, variable=var, command=self.update_platform_options)
            chk.grid(row=7, column=idx, padx=5, pady=2, sticky="w")

        self.schedule_check.grid(row=11, column=0, padx=pad_x, pady=pad_y, sticky="w")
        self.schedule_time_label.grid(row=11, column=1, padx=pad_x, pady=pad_y, sticky="e")
        self.schedule_time_entry.grid(row=11, column=2, padx=pad_x, pady=pad_y, sticky="we")
        self.frequency_label.grid(row=12, column=1, padx=pad_x, pady=pad_y, sticky="e")
        self.frequency_menu.grid(row=12, column=2, padx=pad_x, pady=pad_y, sticky="we")
        self.post_button.grid(row=13, column=1, columnspan=2, pady=20)

    def toggle_media_fields(self):
        mtype = self.media_type_var.get()
        state_img = "normal" if mtype in ["Image", "All"] else "disabled"
        state_vid = "normal" if mtype in ["Video", "All"] else "disabled"
        self.image_path_entry.config(state=state_img)
        self.image_browse.config(state=state_img)
        self.video_path_entry.config(state=state_vid)
        self.video_browse.config(state=state_vid)

    def toggle_schedule(self):
        state = "normal" if self.schedule_var.get() else "disabled"
        self.schedule_time_entry.config(state=state)
        self.frequency_menu.config(state=state)
        if state == "disabled":
            self.schedule_time_entry.delete(0, "end")
            self.frequency_var.set("None")

    def browse_images(self):
        paths = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif")])
        if paths:
            self.image_path_var.set(";".join(paths))

    def browse_videos(self):
        paths = filedialog.askopenfilenames(title="Select Videos", filetypes=[("Video Files", "*.mp4 *.mov *.avi")])
        if paths:
            self.video_path_var.set(";".join(paths))
            
    def update_facebook_story_post_options(self):
        if self.facebook_story_var.get():
            self.facebook_story_frame.pack(anchor="w", padx=10, pady=5)
        else:
            self.facebook_story_frame.pack_forget()

        if self.facebook_post_var.get():
            self.facebook_post_frame.pack(anchor="w", padx=10, pady=5)
        else:
            self.facebook_post_frame.pack_forget()

    def facebook_post_all_override(self):
        if self.facebook_post_options_vars["All"].get():
            # Disable others
            for key in ["Only Text", "Only Image", "Only Video"]:
                self.facebook_post_options_vars[key].set(False)


    def update_platform_options(self):
        # Instagram toggle
        if self.platforms["Instagram"].get():
            self.instagram_frame.grid()
        else:
            self.instagram_frame.grid_remove()
            for var in self.instagram_options_vars.values():
                var.set(False)
            self.instagram_post_orientation.set("")
            self.instagram_reel_orientation.set("")
            self.post_orient_frame.grid_remove()
            self.reel_orient_frame.grid_remove()

        # Twitter toggle
        if self.platforms["Twitter"].get():
            self.twitter_frame.grid()
        else:
            self.twitter_frame.grid_remove()
            for var in self.twitter_options_vars.values():
                var.set(False)
        # LinkedIn toggle
        # Check if LinkedIn platform is selected
        if self.platforms["LinkedIn"].get():
            self.linkedin_frame.grid()  # Show the LinkedIn options frame
        else:
            self.linkedin_frame.grid_remove()  # Hide the LinkedIn options frame
            self.linkedin_options_vars.set(None)# Reset the selected LinkedIn option (since it's a Radiobutton)
            
        # facebook toggle
        if self.platforms["Facebook"].get():
            self.facebook_frame.grid()
        else:
            self.facebook_frame.grid_remove()



    def update_instagram_orientation(self):
        if self.instagram_options_vars["Post"].get():
            self.post_orient_frame.grid()
        else:
            self.post_orient_frame.grid_remove()
            self.instagram_post_orientation.set("")
        if self.instagram_options_vars["Reel"].get():
            self.reel_orient_frame.grid()
        else:
            self.reel_orient_frame.grid_remove()
            self.instagram_reel_orientation.set("")

    def create_post(self):
        # --- Facebook mandatory checks ---
        if self.platforms["Facebook"].get():
            if not (self.facebook_story_var.get() or self.facebook_post_var.get()):
                messagebox.showerror("Error", "For Facebook, select at least Story or Post.")
                return
            
            if self.facebook_story_var.get():
                if not self.facebook_story_var_choice.get():
                    messagebox.showerror("Error", "For Facebook Story, select at least Text Story or Photo Story.")
                    return

            
            if self.facebook_post_var.get():
                if not (any(var.get() for key, var in self.facebook_post_options_vars.items() if key != "All") or self.facebook_post_options_vars["All"].get()):
                    messagebox.showerror("Error", "For Facebook Post, select at least one option (Only Text, Only Image, Only Video, or All).")
                    return
        
        # Your original create_post logic continues...

        # 1) Instagram-specific validation
        if self.platforms["Instagram"].get():
            if (self.instagram_options_vars["Post"].get() 
                and not self.instagram_post_orientation.get()):
                messagebox.showerror(
                    "Error", "Please select orientation for Instagram Post."
                )
                return
            if (self.instagram_options_vars["Reel"].get() 
                and not self.instagram_reel_orientation.get()):
                messagebox.showerror(
                    "Error", "Please select orientation for Instagram Reel."
                )
                return

        # 2) LinkedIn-specific validation
        if self.platforms["LinkedIn"].get():
            linkedin_selected_option = self.linkedin_options_vars.get()
            if linkedin_selected_option == "None":  # No LinkedIn option selected
                messagebox.showerror(
                    "Error", "Please select an option for LinkedIn (Video Only, Only Article, or Image Posts)."
                )
                return

        # 3) Gather inputs (same as before)
        title = self.title_entry.get().strip()
        text = self.text_entry.get("1.0", "end-1c").strip()
        hashtags = self.hashtags_entry.get().strip()
        mtype = self.media_type_var.get()

        # Consolidate media paths
        if mtype == "Image":
            media = self.image_path_var.get().split(";") if self.image_path_var.get() else []
        elif mtype == "Video":
            media = self.video_path_var.get().split(";") if self.video_path_var.get() else []
        elif mtype == "All":
            media = []
            if self.image_path_var.get():
                media += self.image_path_var.get().split(";")
            if self.video_path_var.get():
                media += self.video_path_var.get().split(";")
        else:
            media = []

        platforms = {name: var.get() for name, var in self.platforms.items()}
        instagram_opts = {name: var.get() for name, var in self.instagram_options_vars.items()}
        twitter_opts = {name: var.get() for name, var in self.twitter_options_vars.items()}
        linkedin_opt = self.linkedin_options_vars.get()  # Get the selected LinkedIn option

        post_orient = self.instagram_post_orientation.get()
        reel_orient = self.instagram_reel_orientation.get()

        schedule_flag = self.schedule_var.get()
        schedule_time_str = self.schedule_time_entry.get().strip() if schedule_flag else ""
        frequency = self.frequency_var.get() if schedule_flag else "None"

    # Continue with creating the post...

        # Collect Facebook options
        facebook_options = {
            "story_selected": self.facebook_story_var.get(),
            "post_selected": self.facebook_post_var.get(),
            "story_options": self.facebook_story_var_choice.get(),
            "post_options": {name: var.get() for name, var in self.facebook_post_options_vars.items()}
        }



    # Continue with creating the post...




        # 3) Validation
        if not any(platforms.values()):
            messagebox.showerror("Error", "Please select at least one platform.")
            return
        if not title or not text:
            messagebox.showerror("Error", "Please fill in the title and text.")
            return

        # 4) Build JSON payload and save
        post_data = {
            "title": title,
            "text": text,
            "hashtags": hashtags,
            "media_type": mtype,
            "media_paths": media,
            "platforms": platforms,
            "facebook_options": facebook_options,
            "linkedin_option": linkedin_opt,
            "instagram_options": instagram_opts,
            "instagram_post_orientation": post_orient,
            "instagram_reel_orientation": reel_orient,
            "twitter_options": twitter_opts,
            "schedule_post": schedule_flag,
            "schedule_time": schedule_time_str,
            "repeat_frequency": frequency
        }

        try:
            with open("data/post_data.json", "w") as f:
                json.dump(post_data, f, indent=4)
            messagebox.showinfo("Saved", "All input saved to post_data.json")
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save JSON:\n{e}")
            return

        # 5) Proceed with scheduling or immediate dispatch
        try:
            if schedule_flag:
                sched_dt = datetime.strptime(schedule_time_str, "%Y-%m-%d %H:%M")
                delay = (sched_dt - datetime.now()).total_seconds()
                if delay <= 0:
                    messagebox.showerror("Error", "Scheduled time must be in the future.")
                    return
                schedule_post_with_repeat(delay, frequency, 
                                         [p.lower() for p,v in platforms.items() if v],
                                         title, text, hashtags, media)
                messagebox.showinfo(
                    "Scheduled",
                    f"Post scheduled for {sched_dt.strftime('%Y-%m-%d %H:%M')} "
                    f"with {frequency.lower()} repetition."
                )
            else:
                # new code:
                try:
                    dispatch_post("data/post_data.json")
                    messagebox.showinfo("Success", "Post successfully shared.")
                except Exception as e:
                    messagebox.showerror("Dispatch Failed", str(e))

        except Exception as e:
            messagebox.showerror("Posting Failed", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = PostCreationApp(root)
    root.mainloop()
