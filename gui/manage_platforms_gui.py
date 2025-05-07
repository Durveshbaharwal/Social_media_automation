import os
import json
import gradio as gr
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# Directories and file paths
DATA_DIR = "data"
PROFILE_FILE = os.path.join(DATA_DIR, "profiles.json")
COOKIES_DIR = "cookies"
ALL_PLATFORMS = ["Facebook", "Instagram", "Twitter", "LinkedIn"]
PLATFORM_URLS = {
    "Facebook": "https://www.facebook.com/",
    "Instagram": "https://www.instagram.com/",
    "Twitter": "https://www.twitter.com/",
    "LinkedIn": "https://www.linkedin.com/"
}

# Utility functions
def load_user_profile():
    if not os.path.exists(PROFILE_FILE):
        return None
    with open(PROFILE_FILE, "r") as f:
        return json.load(f)

def save_profile(data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(PROFILE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    return "✅ Profile saved successfully!"

def verify_password(entered, saved):
    return entered == saved  # In production, use proper hashing

# Core application logic

def setup_profile_logic(username, password):
    data = {"name": username, "password": password}
    save_profile(data)
    return data

def perform_post_creation(profile, content):
    # Placeholder: integrate your Selenium automation here if needed
    return {"status": "Posted", "user": profile.get("name"), "content": content}

def open_platform_session_logic(platform):
    profile = load_user_profile()
    if not profile:
        return "❌ No profile found."

    try:
        profile_name = profile.get("name", "").replace(" ", "_")
        cookies_path = os.path.join(os.getcwd(), COOKIES_DIR, profile_name, platform.lower())
        os.makedirs(cookies_path, exist_ok=True)

        options = Options()
        options.add_argument(f"--user-data-dir={cookies_path}")
        options.add_argument("--disable-notifications")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        driver = webdriver.Chrome(options=options)
        driver.get(PLATFORM_URLS[platform])
        driver.quit()
        return f"✅ Opened {platform} session successfully."
    except Exception as e:
        return f"❌ Failed to open {platform}: {str(e)}"

# Gradio handler functions

def profile_setup_handler(username: str, password: str):
    setup_profile_logic(username, password)
    return "✅ Profile set up successfully!"

def create_post_handler(content: str):
    profile = load_user_profile()
    if not profile:
        return {"error": "No profile set up. Please use the Profile Setup tab."}
    return perform_post_creation(profile, content)

def manage_profile_handler(password: str, platform: str):
    profile = load_user_profile()
    if not profile:
        return "❌ No profile set up."
    if not verify_password(password, profile.get("password", "")):
        return "❌ Incorrect password."
    return open_platform_session_logic(platform)

# Build Gradio interface
with gr.Blocks() as demo:
    gr.Markdown("# Social Media Automation (Gradio UI)")

    with gr.Tab("Profile Setup"):
        gr.Markdown("Enter your username and password to create a profile.")
        username_input = gr.Textbox(label="Username")
        password_input = gr.Textbox(label="Password", type="password")
        setup_btn = gr.Button("Save Profile")
        setup_msg = gr.Textbox(label="Status", interactive=False)
        setup_btn.click(fn=profile_setup_handler,
                        inputs=[username_input, password_input],
                        outputs=[setup_msg])

    with gr.Tab("Create Post"):
        gr.Markdown("Write and send a new post.")
        post_input = gr.Textbox(lines=4, label="Post Content")
        post_btn = gr.Button("Create Post")
        post_output = gr.JSON(label="Result JSON")
        post_btn.click(fn=create_post_handler,
                       inputs=[post_input],
                       outputs=[post_output])

    with gr.Tab("Manage Profile"):
        gr.Markdown("Authenticate and open a browser session for your social accounts.")
        password_input2 = gr.Textbox(label="Enter Password", type="password")
        platform_dropdown = gr.Dropdown(choices=ALL_PLATFORMS, label="Select Platform")
        manage_btn = gr.Button("Open Session")
        manage_msg = gr.Textbox(label="Status", interactive=False)
        manage_btn.click(fn=manage_profile_handler,
                         inputs=[password_input2, platform_dropdown],
                         outputs=[manage_msg])

# Launch the Gradio app
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
