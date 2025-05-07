import os
import json
import gradio as gr

# TODO: Replace these stubs with your actual business-logic implementations
#       currently encapsulated inside your tkinter GUI classes.
from automation_core import (
    setup_profile_logic,
    manage_platforms_logic,
    perform_post_creation
)

# Path to store profile data
data_dir = "data"
PROFILE_FILE = os.path.join(data_dir, "profiles.json")

# Load existing profile at startup (if any)
def load_profile():
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f:
            return json.load(f)
    return None

profile = load_profile()

# Save profile to disk and update in-memory state
def save_profile(data):
    os.makedirs(os.path.dirname(PROFILE_FILE), exist_ok=True)
    with open(PROFILE_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    global profile
    profile = data
    return "✅ Profile saved successfully!"

# Gradio handler: Profile setup
def profile_setup_handler(username: str):
    # Call your extraction of logic from ProfileSetupApp here
    data = setup_profile_logic(username)
    msg = save_profile(data)
    return msg

# Gradio handler: Manage existing profile
def manage_profile_handler():
    if not profile:
        return "⚠️ No profile found. Please set up a profile first."
    data = manage_platforms_logic(profile)
    msg = save_profile(data)
    return msg

# Gradio handler: Create a new post
def create_post_handler(content: str):
    if not profile:
        return {"error": "No profile set up. Please go to the Profile Setup tab."}
    result = perform_post_creation(profile, content)
    return result

# Build Gradio interface
demo = gr.Blocks()

with demo:
    gr.Markdown("# Social Media Automation (Gradio UI)")
    
    with gr.Tab("Profile Setup"):
        gr.Markdown("Set up your social media profile to get started.")
        username_input = gr.Textbox(label="Username", placeholder="Enter your username")
        setup_btn = gr.Button("Save Profile")
        setup_msg = gr.Textbox(label="Status", interactive=False)
        setup_btn.click(fn=profile_setup_handler,
                        inputs=[username_input],
                        outputs=[setup_msg])

    with gr.Tab("Create Post"):
        gr.Markdown(lambda: f"**Welcome back, {profile['username']}!**" if profile else "**Please set up a profile first.**")
        post_input = gr.Textbox(lines=4, label="Post Content", placeholder="Write your post here...")
        post_btn = gr.Button("Create Post")
        post_output = gr.JSON(label="Result JSON")
        post_btn.click(fn=create_post_handler,
                       inputs=[post_input],
                       outputs=[post_output])

    with gr.Tab("Manage Profile"):
        gr.Markdown("Review and update your linked platforms.")
        manage_btn = gr.Button("Manage Platforms")
        manage_msg = gr.Textbox(label="Status", interactive=False)
        manage_btn.click(fn=manage_profile_handler,
                         inputs=None,
                         outputs=[manage_msg])

# Launch the Gradio app
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
