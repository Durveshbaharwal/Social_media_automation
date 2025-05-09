import gradio as gr
import json
import datetime
import os
from dispatcher.post_dispatcher import dispatch_post
from datetime import datetime

def browse_images():
    return gr.inputs.File(label="Select Images", file_count="multiple", type="file")

def browse_videos():
    return gr.inputs.File(label="Select Videos", file_count="multiple", type="file")

def create_post(title, text, hashtags, media_type, images, videos, platforms, schedule, schedule_time, frequency):
    # Validation checks (same as the original code)
    if not any(platforms.values()):
        return "Error: Please select at least one platform."

    if not title or not text:
        return "Error: Please fill in the title and text."

    # Prepare media files based on the media type
    media = []
    if media_type == "Image" and images:
        media = [image.name for image in images]
    elif media_type == "Video" and videos:
        media = [video.name for video in videos]
    elif media_type == "All":
        if images:
            media.extend([image.name for image in images])
        if videos:
            media.extend([video.name for video in videos])

    post_data = {
        "title": title,
        "text": text,
        "hashtags": hashtags,
        "media_type": media_type,
        "media_paths": media,
        "platforms": platforms,
        "schedule_post": schedule,
        "schedule_time": schedule_time,
        "repeat_frequency": frequency
    }

    try:
        with open("data/post_data.json", "w") as f:
            json.dump(post_data, f, indent=4)
        return "All input saved to post_data.json"
    except Exception as e:
        return f"Error: Could not save JSON: {e}"

def platform_selection(*args):
    # This function can update available platform options based on the selected platforms
    return {platform: selected for platform, selected in zip(
        ["Facebook", "Instagram", "Twitter", "LinkedIn"], args)}

with gr.Blocks() as app:
    gr.Markdown("# Create New Post")

    with gr.Row():
        title = gr.Textbox(label="Post Title:")
        text = gr.Textbox(label="Post Text:", lines=5)
        hashtags = gr.Textbox(label="Hashtags:")

    media_type = gr.Dropdown(
        choices=["None", "Image", "Video", "All"],
        value="None",
        label="Media Type"
    )

    images = browse_images()
    videos = browse_videos()

    platforms = {
        "Facebook": gr.Checkbox(label="Facebook", value=False),
        "Instagram": gr.Checkbox(label="Instagram", value=False),
        "Twitter": gr.Checkbox(label="Twitter", value=False),
        "LinkedIn": gr.Checkbox(label="LinkedIn", value=False)
    }

    schedule = gr.Checkbox(label="Schedule Post", value=False)
    schedule_time = gr.Textbox(label="Schedule Time (YYYY-MM-DD HH:MM):")
    frequency = gr.Dropdown(choices=["None", "Daily", "Weekly"], value="None", label="Repeat Frequency")

    post_button = gr.Button("Post")

    post_button.click(
        create_post,
        inputs=[title, text, hashtags, media_type, images, videos, platforms, schedule, schedule_time, frequency],
        outputs="text"
    )

    platforms_selection = gr.Row([
        gr.Checkbox(label="Facebook"),
        gr.Checkbox(label="Instagram"),
        gr.Checkbox(label="Twitter"),
        gr.Checkbox(label="LinkedIn")
    ])

app.launch()
