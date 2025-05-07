import os
import json
import datetime
import gradio as gr
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from dispatcher.post_dispatcher import dispatch_post

# Directories
DATA_DIR = "data"
PROFILE_FILE = os.path.join(DATA_DIR, "profiles.json")
POST_DATA_FILE = os.path.join(DATA_DIR, "post_data.json")
os.makedirs(DATA_DIR, exist_ok=True)

# Platform URLs
PLATFORM_URLS = {
    "Facebook": "https://www.facebook.com/",
    "Instagram": "https://www.instagram.com/",
    "Twitter": "https://www.twitter.com/",
    "LinkedIn": "https://www.linkedin.com/"
}

# Profile Data Handlers
 def save_profile_data(profile):
    with open(PROFILE_FILE, "w") as f:
        json.dump(profile, f, indent=4)
    return {"status": "Profile saved."}

def load_profile_data():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, "r") as f:
            return json.load(f)
    return None

# Selenium Login
 def login_to_platforms(selected_platforms, name):
    messages = []
    cookies_base = os.path.join(os.getcwd(), 'cookies', name.replace(" ", "_"))
    for platform in selected_platforms:
        try:
            path = os.path.join(cookies_base, platform.lower())
            os.makedirs(path, exist_ok=True)
            opts = Options()
            opts.add_argument(f"--user-data-dir={path}")
            opts.add_argument("--disable-notifications")
            opts.add_argument("--start-maximized")
            driver = webdriver.Chrome(options=opts)
            driver.get(PLATFORM_URLS[platform])
            driver.quit()
            messages.append(f"✅ Logged into {platform}.")
        except Exception as e:
            messages.append(f"❌ {platform}: {e}")
    return {"messages": messages}

# Post Dispatcher
 def create_post_handler(
    title, text, hashtags, mtype, images, videos,
    platforms, fb_story, fb_post, fb_story_opt, fb_post_opts,
    insta_opts, insta_post_orient, insta_reel_orient,
    twitter_opts, linkedin_opt,
    schedule_flag, schedule_time, frequency
):
    # (reuse existing validation and save logic)
    # For brevity, refer to previous create_post_handler implementation
    return dispatch_post_logic(title, text, hashtags, mtype, images, videos,
                                 platforms, fb_story, fb_post, fb_story_opt, fb_post_opts,
                                 insta_opts, insta_post_orient, insta_reel_orient,
                                 twitter_opts, linkedin_opt,
                                 schedule_flag, schedule_time, frequency)

# Existing authentication
 def authenticate_user(username, password):
    profile = load_profile_data()
    if profile and profile.get("username") == username and profile.get("password") == password:
        return {"status": f"Welcome back, {profile.get('name')}!"}
    return {"error": "Invalid credentials."}

# Build Gradio App
with gr.Blocks() as demo:
    gr.Markdown("# Social Media Automation")
    with gr.Tab("Profile Setup"):
        with gr.Tabs():
            with gr.TabItem("Login Existing"):
                li_user = gr.Textbox(label="Username")
                li_pass = gr.Textbox(label="Password", type="password")
                li_btn = gr.Button("Login")
                li_out = gr.JSON()
                li_btn.click(fn=authenticate_user, inputs=[li_user, li_pass], outputs=[li_out])
            with gr.TabItem("Create New"):
                name = gr.Textbox(label="Your Name")
                un = gr.Textbox(label="Login ID")
                pw = gr.Textbox(label="Password", type="password")
                show_pw = gr.Checkbox(label="Show Password")
                plt = gr.CheckboxGroup(label="Select Platforms", choices=list(PLATFORM_URLS.keys()))
                login_btn = gr.Button("Login to Platforms")
                login_out = gr.JSON()
                save_btn = gr.Button("Save Profile")
                save_out = gr.JSON()

                # Toggle password visibility client-side
                show_pw.change(lambda s: {"type": "password" if not s else "text"}, inputs=[show_pw], outputs=[pw])
                login_btn.click(fn=lambda pl, nm: login_to_platforms(pl, nm), inputs=[plt, name], outputs=[login_out])
                save_btn.click(fn=lambda nm, unv, pwv, pl: save_profile_data({
                    "name": nm, "username": unv, "password": pwv, "platforms": pl
                }), inputs=[name, un, pw, plt], outputs=[save_out])

    with gr.Tab("Create Post"):
        # reuse the existing Create Post UI
        # [insert previous Blocks code for Create New Post here]
        gr.Markdown("_Post creation UI goes here..._")

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
