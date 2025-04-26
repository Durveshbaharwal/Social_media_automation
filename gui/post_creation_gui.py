import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import datetime
from utils.scheduler import schedule_post_with_repeat
from dispatcher.post_dispatcher import dispatch_post
from utils.logger import log_post

class PostCreationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Create New Post")
        self.root.geometry("600x700")

        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        # Title
        self.title_label = tk.Label(root, text="Post Title:")
        self.title_entry = tk.Entry(root)

        # Text
        self.text_label = tk.Label(root, text="Post Text:")
        self.text_entry = tk.Text(root, height=5)

        # Hashtags
        self.hashtags_label = tk.Label(root, text="Hashtags:")
        self.hashtags_entry = tk.Entry(root)

        # Media type
        self.media_type_label = tk.Label(root, text="Media Type:")
        self.media_type_var = tk.StringVar(value="None")
        self.media_types = ["None", "Image", "Video", "All"]
        self.media_type_menu = ttk.Combobox(root, textvariable=self.media_type_var,
                                            values=self.media_types, state="readonly")
        self.media_type_menu.bind("<<ComboboxSelected>>", lambda e: self.toggle_media_fields())

        # Image
        self.image_path_label = tk.Label(root, text="Select Images:")
        self.image_path_var = tk.StringVar()
        self.image_path_entry = tk.Entry(root, textvariable=self.image_path_var)
        self.image_browse = tk.Button(root, text="Browse Images", command=self.browse_images)

        # Video
        self.video_path_label = tk.Label(root, text="Select Videos:")
        self.video_path_var = tk.StringVar()
        self.video_path_entry = tk.Entry(root, textvariable=self.video_path_var)
        self.video_browse = tk.Button(root, text="Browse Videos", command=self.browse_videos)
        
                # Twitter options
        self.twitter_options = {
            "Only Text": tk.BooleanVar(),
            "Only Videos": tk.BooleanVar(),
            "Only Images": tk.BooleanVar(),
            "All": tk.BooleanVar()
        }

        # Instagram options
        self.instagram_options = {
            "Post": tk.BooleanVar(),
            "Reel": tk.BooleanVar(),
            "Story": tk.BooleanVar()
        }
        self.instagram_orientation = tk.StringVar(value="")  # For Post or Reel


        # Platforms
        self.platforms_label = tk.Label(root, text="Select Platforms:")
        self.platforms = {
            "Facebook": tk.BooleanVar(),
            "Instagram": tk.BooleanVar(),
            "Twitter": tk.BooleanVar(),
            "LinkedIn": tk.BooleanVar()
        }

        # Scheduling
        self.schedule_var = tk.BooleanVar()
        self.schedule_check = tk.Checkbutton(root, text="Schedule Post", variable=self.schedule_var,
                                             command=self.toggle_schedule)
        self.schedule_time_label = tk.Label(root, text="Schedule Time (YYYY-MM-DD HH:MM):")
        self.schedule_time_entry = tk.Entry(root)
        self.frequency_label = tk.Label(root, text="Repeat Frequency:")
        self.frequency_options = ["None", "Daily", "Weekly"]
        self.frequency_var = tk.StringVar(value="None")
        self.frequency_menu = ttk.Combobox(root, textvariable=self.frequency_var,
                                           values=self.frequency_options, state="readonly")

        # Post button
        self.post_button = tk.Button(root, text="Post", command=self.create_post)

        # Layout
        self.layout_widgets()
        self.toggle_media_fields()
        self.toggle_schedule()

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
            chk = tk.Checkbutton(self.root, text=name, variable=var)
            chk.grid(row=7 + idx, column=0, padx=20, pady=2, sticky="w")
            
            
        # Twitter-specific options
        tk.Label(self.root, text="Twitter Options:").grid(row=7, column=1, sticky="w", padx=10)
        for idx, (name, var) in enumerate(self.twitter_options.items()):
            tk.Checkbutton(self.root, text=name, variable=var).grid(row=8+idx, column=1, sticky="w", padx=20)

        # Instagram-specific options
        tk.Label(self.root, text="Instagram Options:").grid(row=12, column=0, sticky="w", padx=10)
        for idx, (name, var) in enumerate(self.instagram_options.items()):
            chk = tk.Checkbutton(self.root, text=name, variable=var, command=self.update_instagram_options)
            chk.grid(row=13+idx, column=0, sticky="w", padx=20)

        # Instagram orientation radio buttons
        self.orientation_frame = tk.Frame(self.root)
        self.orientation_label = tk.Label(self.orientation_frame, text="Select Orientation:")
        self.orientation_label.pack(anchor="w")
        for orient in ["Square", "Landscape", "Portrait"]:
            tk.Radiobutton(self.orientation_frame, text=orient, variable=self.instagram_orientation, value=orient).pack(anchor="w")
        self.orientation_frame.grid(row=16, column=0, columnspan=3, sticky="w", padx=20, pady=(0,10))
        self.orientation_frame.grid_remove()  # Hide by default


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
        
    def update_instagram_options(self):
        show_orientation = self.instagram_options["Post"].get() or self.instagram_options["Reel"].get()
        if show_orientation:
            self.orientation_frame.grid()
        else:
            self.orientation_frame.grid_remove()
            self.instagram_orientation.set("")


    def toggle_schedule(self):
        state = "normal" if self.schedule_var.get() else "disabled"
        self.schedule_time_entry.config(state=state)
        self.frequency_menu.config(state=state)
        if state == "disabled":
            self.schedule_time_entry.delete(0, "end")
            self.frequency_var.set("None")

    def browse_images(self):
        paths = filedialog.askopenfilenames(
            title="Select Images",
            filetypes=[("Image Files", "*.jpg *.jpeg *.png *.gif")]
        )
        if paths:
            self.image_path_var.set(";".join(paths))

    def browse_videos(self):
        paths = filedialog.askopenfilenames(
            title="Select Videos",
            filetypes=[("Video Files", "*.mp4 *.mov *.avi")]
        )
        if paths:
            self.video_path_var.set(";".join(paths))

    def create_post(self):
        title = self.title_entry.get().strip()
        text = self.text_entry.get("1.0", "end-1c").strip()
        hashtags = self.hashtags_entry.get().strip()
        mtype = self.media_type_var.get()
        media = ""

        if mtype == "Image":
            media = self.image_path_var.get().strip()
        elif mtype == "Video":
            media = self.video_path_var.get().strip()
        elif mtype == "All":
            img = self.image_path_var.get().strip()
            vid = self.video_path_var.get().strip()
            media = ";".join([x for x in [img, vid] if x])


        selected_platforms = [name.lower() for name, var in self.platforms.items() if var.get()]
        if not selected_platforms:
            messagebox.showerror("Error", "Please select at least one platform.")
            return
        if not title or not text:
            messagebox.showerror("Error", "Please fill in the title and text.")
            return

        try:
            if self.schedule_var.get():
                schedule_str = self.schedule_time_entry.get().strip()
                schedule_time = datetime.strptime(schedule_str, "%Y-%m-%d %H:%M")
                delay = (schedule_time - datetime.now()).total_seconds()
                if delay <= 0:
                    messagebox.showerror("Error", "Scheduled time must be in the future.")
                    return
                frequency = self.frequency_var.get()
                schedule_post_with_repeat(delay, frequency, selected_platforms, title, text, hashtags, media)
                messagebox.showinfo(
                    "Scheduled",
                    f"Post scheduled for {schedule_time.strftime('%Y-%m-%d %H:%M')} with {frequency.lower()} repetition."
                )
            else:
                failed = dispatch_post(selected_platforms, title, text, hashtags, media)
                log_post(title, text, hashtags, media, selected_platforms, failed)
                if failed:
                    messagebox.showwarning(
                        "Partial Success",
                        f"Posted to some platforms but failed: {', '.join(failed)}"
                    )
                else:
                    messagebox.showinfo("Success", "Post successfully shared.")
        except Exception as e:
            messagebox.showerror("Posting Failed", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = PostCreationApp(root)
    root.mainloop()
