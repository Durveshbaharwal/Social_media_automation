def log_post(title, text, hashtags, media_path, platforms, failed_platforms):
    log_data = {
        "title": title,
        "text": text,
        "hashtags": hashtags,
        "media_path": media_path,
        "platforms": platforms,
        "failed_platforms": failed_platforms,
        "timestamp": datetime.now().isoformat()
    }

    os.makedirs("logs", exist_ok=True)

    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r") as f:
            logs = json.load(f)
    else:
        logs = []

    logs.append(log_data)

    with open(LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)
