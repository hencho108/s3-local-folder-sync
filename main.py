import argparse
import logging
import threading
import time

import config
import log_config
import sync

# Load configuration
cfg = config.load_config("config.yml")

# Setup logging
log_config.setup_logging(cfg.logging)


if __name__ == "__main__":
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description="Source of the initial sync on start up"
    )
    parser.add_argument(
        "--initial-sync-source",
        type=str,
        default="auto",
        choices=["auto", "local", "s3"],
        help="Set the source of the initial sync on start up (default: auto based on timestamps)",
    )

    # Parse arguments
    args = parser.parse_args()

    # Perform initial sync
    sync.initial_sync(
        cfg.general.local_folder,
        cfg.general.s3_bucket,
        cfg.sync.sync_deletions,
        args.initial_sync_source,
    )

    # Start the periodic sync in its own thread
    sync_thread = threading.Thread(
        target=sync.periodic_sync,
        args=(
            cfg.general.local_folder,
            cfg.general.s3_bucket,
            cfg.sync.sync_deletions,
            cfg.sync.interval,
        ),
    )
    sync_thread.daemon = True  # Makes the thread a daemon thread
    sync_thread.start()

    # Keep the main thread active
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Program interrupted by user, exiting gracefully...")
