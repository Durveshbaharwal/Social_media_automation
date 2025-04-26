import threading
import datetime
import time
from dispatcher.post_dispatcher import dispatch_post
from utils.logger import log_post

def schedule_post_with_repeat(initial_delay_seconds, frequency, platforms, title, text, hashtags, media_path):
    def job():
        print("[⏰] Scheduled post executing...")
        result = dispatch_post(platforms, title, text, hashtags, media_path)
        log_post(title, text, hashtags, media_path, platforms, result)

    def repeat_job():
        job()  # Run the post job
        if frequency == "Daily":
            delay = 86400  # 24 hours in seconds
        elif frequency == "Weekly":
            delay = 604800  # 7 days in seconds
        else:
            return  # No repeat, so exit
        threading.Timer(delay, repeat_job).start()

    # First, delay for the initial schedule
    threading.Timer(initial_delay_seconds, repeat_job).start()
