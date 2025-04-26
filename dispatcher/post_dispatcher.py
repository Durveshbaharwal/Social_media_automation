import subprocess 
import os
import sys
import json

# Single‐script platforms
PLATFORM_SCRIPTS = {
    "twitter":  "platforms/twitter.py",
    "linkedin": "platforms/linkedin.py"
}

# Instagram splits into 3
INSTAGRAM_SCRIPTS = {
    "Post":  "platforms/instagram_post.py",
    "Reel":  "platforms/instagram_reel.py",
    "Story": "platforms/instagram_story.py"
}

def run_script(script_path, args, label, failed):
    """
    Helper to run `python script_path ...args` and on error append `label` to failed.
    """
    if not os.path.exists(script_path):
        print(f"[!] Script not found: {script_path}")
        failed.append(label)
        return

    try:
        print(f"[→] Dispatching {label} using {script_path}")
        subprocess.run(["python", script_path, *args], check=True)
        print(f"[✓] {label} succeeded")
    except subprocess.CalledProcessError as e:
        print(f"[X] {label} failed: {e}")
        failed.append(label)

def dispatch_post(json_path):
    if not os.path.exists(json_path):
        print(f"[!] JSON file not found: {json_path}")
        sys.exit(1)

    with open(json_path, "r") as f:
        data = json.load(f)

    title       = data.get("title", "")
    text        = data.get("text", "")
    hashtags    = data.get("hashtags", "")
    media_list  = data.get("media_paths", [])
    media_path  = ";".join(media_list) if isinstance(media_list, list) else str(media_list)

    selected_platforms = [
        name for name, enabled in data.get("platforms", {}).items() if enabled
    ]

    if not selected_platforms:
        print("[!] No platforms selected in JSON—nothing to do.")
        return

    failed = []

    for platform in selected_platforms:
        key = platform.lower()

        # 1) LinkedIn – multi-option loop
        if key == "linkedin":
            script = PLATFORM_SCRIPTS[key]
            linkedin_option = data.get("linkedin_option", "None")  # Default to "None" if not provided

            # Check if LinkedIn option is valid
            valid_options = ["Image Posts", "Video Only", "Only Article", "None"]
            
            if linkedin_option not in valid_options:
                print(f"[!] Invalid LinkedIn option: {linkedin_option}. Defaulting to 'None'.")
                linkedin_option = "None"

            # Only proceed if a valid LinkedIn option was found (other than "None")
            if linkedin_option != "None":
                args = [title, text, hashtags, media_path, linkedin_option]
                
                # If the option is "Only Article", only post the caption without media
                if linkedin_option == "Only Article":
                    args = [title, text, hashtags, "", linkedin_option]  # Pass empty string for media_path
                
                run_script(
                    script_path=script,
                    args=args,
                    label=f"LinkedIn-{linkedin_option}",
                    failed=failed
                )
            else:
                print("[!] LinkedIn option is 'None'. Skipping LinkedIn post.")



        # 2) Twitter – multi-flag single call
        elif key == "twitter":
            script = PLATFORM_SCRIPTS[key]
            args = [title, text, hashtags, media_path]

            twitter_opts = data.get("twitter_options", {})
            only_text   = twitter_opts.get("Only Text", False)
            only_videos = twitter_opts.get("Only Videos", False)
            only_images = twitter_opts.get("Only Images", False)
            all_media   = twitter_opts.get("All", False)

            if all_media:
                only_text = only_videos = only_images = True

            args += [str(only_text), str(only_videos), str(only_images), str(all_media)]

            run_script(
                script_path=script,
                args=args,
                label=platform,
                failed=failed
            )

        # 3) Instagram – by sub-type
        elif key == "instagram":
            opts = data.get("instagram_options", {})
            post_orient = data.get("instagram_post_orientation", "")
            reel_orient = data.get("instagram_reel_orientation", "")

            for opt_name, enabled in opts.items():
                if not enabled:
                    continue

                script = INSTAGRAM_SCRIPTS.get(opt_name)
                if not script:
                    print(f"[!] No script mapped for Instagram option: {opt_name}")
                    failed.append(f"Instagram-{opt_name}")
                    continue

                args = [title, text, hashtags, media_path]
                if opt_name == "Post":
                    args.append(post_orient)
                elif opt_name == "Reel":
                    args.append(reel_orient)

                run_script(
                    script_path=script,
                    args=args,
                    label=f"Instagram-{opt_name}",
                    failed=failed
                )
                
        elif key == "facebook":
            facebook_opts = data.get("facebook_options", {})

            story_selected = facebook_opts.get("story_selected", False)
            post_selected = facebook_opts.get("post_selected", False)
            story_option = facebook_opts.get("story_options", "")
            post_options = facebook_opts.get("post_options", {})

            if story_selected:
                # Assuming you have a separate script for Facebook stories
                story_script = "platforms/facebook_story.py"
                args = [title, text, hashtags, media_path, story_option]
                run_script(
                    script_path=story_script,
                    args=args,
                    label="Facebook-Story",
                    failed=failed
                )

            if post_selected:
                # Assuming you have a separate script for Facebook posts
                post_script = "platforms/facebook_post.py"

                # Pass post options as arguments if needed (currently optional)
                only_text = str(post_options.get("Only Text", False))
                only_image = str(post_options.get("Only Image", False))
                only_video = str(post_options.get("Only Video", False))
                all_media = str(post_options.get("All", False))

                args = [title, text, hashtags, media_path, only_text, only_image, only_video, all_media]

                run_script(
                    script_path=post_script,
                    args=args,
                    label="Facebook-Post",
                    failed=failed
                )


        # 4) All other platforms
        elif key in PLATFORM_SCRIPTS:
            script = PLATFORM_SCRIPTS[key]
            args = [title, text, hashtags, media_path]

            run_script(
                script_path=script,
                args=args,
                label=platform,
                failed=failed
            )

        else:
            print(f"[!] Unsupported platform in JSON: {platform}")
            failed.append(platform)

    if failed:
        print(f"[!] Dispatch completed, but failures on: {', '.join(failed)}")
    else:
        print("[✓] Dispatch completed successfully for all selected tasks.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python dispatcher.py <path/to/post_data.json>")
        sys.exit(1)

    dispatch_post(sys.argv[1])
