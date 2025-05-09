import gradio as gr
import os
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import subprocess

# Constants
PROFILE_FILE = "data/profiles.json"

def load_profile():
    with open(PROFILE_FILE, "r") as f:
        return json.load(f)

def launch_browser(platform):
    try:
        profile = load_profile()
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
        return f"Launched {platform} login in browser."
    except Exception as e:
        return f"Error launching browser for {platform}: {e}"

def save_and_exit():
    # In a Gradio app, there's no "exit" in the traditional sense.
    return "Changes saved. You can now close this tab."

def save_and_start_posting():
    try:
        subprocess.Popen(["python", "gui/new_gui_post.py"])
        return "Launching posting interface..."
    except Exception as e:
        return f"Failed to launch posting interface: {e}"

# Gradio Interface
def manage_platforms_ui():
    with gr.Blocks() as demo:
        gr.Markdown("## Log in to your Platforms")

        with gr.Row():
            for platform in ["Facebook", "Instagram", "LinkedIn", "Twitter"]:
                gr.Button(f"Login to {platform}").click(
                    fn=launch_browser,
                    inputs=[],
                    outputs=gr.Textbox(label="", interactive=False),
                    _js=f"() => '{platform}'"
                )

        with gr.Row():
            gr.Button("Save and Exit").click(fn=save_and_exit, inputs=[], outputs=gr.Textbox(label="", interactive=False))
            gr.Button("Save and Start Posting").click(fn=save_and_start_posting, inputs=[], outputs=gr.Textbox(label="", interactive=False))

    return demo

if __name__ == "__main__":
    ui = manage_platforms_ui()
    ui.launch()
