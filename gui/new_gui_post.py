import os
import json
import gradio as gr
import datetime
from dispatcher.post_dispatcher import dispatch_post

# Data directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)
POST_DATA_FILE = os.path.join(DATA_DIR, "post_data.json")

# Validation helper
def validate_inputs(inputs):
    (
        title, text, hashtags, mtype, images, videos,
        platforms, fb_story, fb_post, fb_story_opt, fb_post_opts,
        insta_opts, insta_post_orient, insta_reel_orient,
        twitter_opts, linkedin_opt,
        schedule_flag, schedule_time, frequency
    ) = inputs

    # Basic checks
    if not any(platforms.values()):
        return False, "Please select at least one platform."
    if not title.strip():
        return False, "Please enter a title."
    if not text.strip():
        return False, "Please enter post text."

    # Facebook checks
    if platforms.get("Facebook"):
        if not (fb_story or fb_post):
            return False, "For Facebook, select Story or Post."
        if fb_story and not fb_story_opt:
            return False, "Select a Facebook Story option."
        if fb_post and not any(fb_post_opts.values()):
            return False, "Select at least one Facebook Post option."

    # Instagram checks
    if platforms.get("Instagram"):
        if insta_opts.get("Post") and not insta_post_orient:
            return False, "Select Instagram Post orientation."
        if insta_opts.get("Reel") and not insta_reel_orient:
            return False, "Select Instagram Reel orientation."

    # LinkedIn checks
    if platforms.get("LinkedIn") and not linkedin_opt:
        return False, "Select a LinkedIn option."

    # Schedule time check
    if schedule_flag:
        try:
            sched_dt = datetime.datetime.strptime(schedule_time, "%Y-%m-%d %H:%M")
            if sched_dt <= datetime.datetime.now():
                return False, "Scheduled time must be in the future."
        except Exception:
            return False, "Schedule time must match YYYY-MM-DD HH:MM format."

    return True, None

# Handler function

def create_post_handler(
    title, text, hashtags, mtype, images, videos,
    platforms, fb_story, fb_post, fb_story_opt, fb_post_opts,
    insta_opts, insta_post_orient, insta_reel_orient,
    twitter_opts, linkedin_opt,
    schedule_flag, schedule_time, frequency
):
    inputs = (
        title, text, hashtags, mtype, images, videos,
        platforms, fb_story, fb_post, fb_story_opt, fb_post_opts,
        insta_opts, insta_post_orient, insta_reel_orient,
        twitter_opts, linkedin_opt,
        schedule_flag, schedule_time, frequency
    )
    valid, error = validate_inputs(inputs)
    if not valid:
        return {"error": error}

    # Consolidate media paths
    media = []
    if mtype in ["Image", "All"] and images:
        media += [f.name for f in images]
    if mtype in ["Video", "All"] and videos:
        media += [f.name for f in videos]

    post_data = {
        "title": title.strip(),
        "text": text.strip(),
        "hashtags": hashtags.strip(),
        "media_type": mtype,
        "media_paths": media,
        "platforms": platforms,
        "facebook_options": {
            "story": fb_story,
            "post": fb_post,
            "story_option": fb_story_opt,
            "post_options": fb_post_opts
        },
        "instagram_options": insta_opts,
        "instagram_post_orientation": insta_post_orient,
        "instagram_reel_orientation": insta_reel_orient,
        "twitter_options": twitter_opts,
        "linkedin_option": linkedin_opt,
        "schedule_post": schedule_flag,
        "schedule_time": schedule_time,
        "repeat_frequency": frequency
    }

    # Save to file
    try:
        with open(POST_DATA_FILE, "w") as f:
            json.dump(post_data, f, indent=4)
    except Exception as e:
        return {"error": f"Failed to save JSON: {e}"}

    # Dispatch or schedule
    if schedule_flag:
        # Scheduling not implemented yet
        return {"status": "Scheduled for future posting (feature pending)."}
    else:
        try:
            dispatch_post(POST_DATA_FILE)
            return {"status": "Post successfully shared."}
        except Exception as e:
            return {"error": str(e)}

# Build Gradio UI
with gr.Blocks() as demo:
    gr.Markdown("# Create New Post")
    with gr.Row():
        title = gr.Textbox(label="Post Title")
        hashtags = gr.Textbox(label="Hashtags (comma-separated)")
    text = gr.Textbox(label="Post Text", lines=5)
    mtype = gr.Dropdown(label="Media Type", choices=["None", "Image", "Video", "All"], value="None")
    images = gr.File(label="Upload Images", file_count="multiple", type="file")
    videos = gr.File(label="Upload Videos", file_count="multiple", type="file")

    platforms = gr.CheckboxGroup(label="Select Platforms", choices=["Facebook","Instagram","Twitter","LinkedIn"])

    # Facebook options
    fb_story = gr.Checkbox(label="Facebook Story")
    fb_post = gr.Checkbox(label="Facebook Post")
    fb_story_opt = gr.Radio(label="Facebook Story Option", choices=["Text Story","Photo Story"], value=None)
    fb_post_opts = gr.CheckboxGroup(label="Facebook Post Options", choices=["Only Text","Only Image","Only Video","All"])

    # Instagram options
    insta_opts = gr.CheckboxGroup(label="Instagram Options", choices=["Post","Reel","Story"])
    insta_post_orient = gr.Radio(label="Instagram Post Orientation", choices=["Square","Landscape","Portrait"], value=None)
    insta_reel_orient = gr.Radio(label="Instagram Reel Orientation", choices=["Square","Landscape","Portrait"], value=None)

    # Twitter options
    twitter_opts = gr.CheckboxGroup(label="Twitter Options", choices=["Only Text","Only Images","Only Videos","All"])

    # LinkedIn options
    linkedin_opt = gr.Radio(label="LinkedIn Option", choices=["Video Only","Only Article","Image Posts"], value=None)

    # Scheduling
    schedule_flag = gr.Checkbox(label="Schedule Post")
    schedule_time = gr.Textbox(label="Schedule Time (YYYY-MM-DD HH:MM)")
    frequency = gr.Dropdown(label="Repeat Frequency", choices=["None","Daily","Weekly"], value="None")

    submit = gr.Button("Post")
    output = gr.JSON(label="Result")
    submit.click(
        fn=create_post_handler,
        inputs=[title, text, hashtags, mtype, images, videos,
                {
                    "Facebook": gr.update(lambda choices: "Facebook" in choices),
                },
                fb_story, fb_post, fb_story_opt, fb_post_opts,
                insta_opts, insta_post_orient, insta_reel_orient,
                twitter_opts, linkedin_opt,
                schedule_flag, schedule_time, frequency],
        outputs=[output]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
