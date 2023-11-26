"""The entry point of the script, setting up the watchdog and the main loop."""
import logging
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import config
import log_config
import sync

# Load configuration
config = config.load_config("config.yml")
local_folder = config["general"]["local_folder"]
s3_bucket = config["general"]["s3_bucket"]
sync_deletions = config["sync"]["sync_deletions"]
s3_to_local_sync_interval = config["sync"]["s3_to_local_sync_interval"]

# Setup logging
log_config.setup_logging(config["logging"])


class ChangeHandler(FileSystemEventHandler):
    def on_any_event(self, event):
        if not event.is_directory:
            sync.sync_files(local_folder, s3_bucket, sync_deletions)


event_handler = ChangeHandler()
observer = Observer()
observer.schedule(event_handler, path=local_folder, recursive=True)

if __name__ == "__main__":
    try:
        logging.info("Monitoring for changes. Press Ctrl+C to stop.")
        observer.start()
        while True:
            # Perform sync from S3 to local in regular intervals
            sync.sync_files(s3_bucket, local_folder, sync_deletions)
            time.sleep(s3_to_local_sync_interval)
    except KeyboardInterrupt:
        observer.stop()
        observer.join()
        logging.info("Stopped monitoring.")
    except Exception as e:
        logging.error(f"Error in main monitoring loop: {e}")
        observer.stop()
        observer.join()
