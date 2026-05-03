import os
import time
import logging

_last_cleanup_at = 0
CLEANUP_INTERVAL_SECONDS = 60 * 10


def cleanup_old_uploads(upload_dir, retention_hours=24):
    global _last_cleanup_at

    now = time.time()
    if now - _last_cleanup_at < CLEANUP_INTERVAL_SECONDS:
        return

    _last_cleanup_at = now
    max_age = retention_hours * 3600

    if not os.path.isdir(upload_dir):
        return

    removed = 0
    for name in os.listdir(upload_dir):
        path = os.path.join(upload_dir, name)
        if not os.path.isfile(path):
            continue
        try:
            if now - os.path.getmtime(path) > max_age:
                os.remove(path)
                removed += 1
        except OSError:
            continue

    if removed:
        logging.info("Upload cleanup removed %s old files", removed)
