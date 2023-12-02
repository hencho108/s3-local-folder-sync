# Simple Sync between Local Folder and S3 Bucket

This project provides a Python-based solution to continuously synchronize a local folder with an Amazon S3 bucket. It acts as a wrapper for the AWS CLI's sync command, extending its functionality with periodic syncing, custom initial sync direction, and enhanced logging.

## Features

- **Periodic Syncing:** Automatically syncs the local folder and the S3 bucket at configurable intervals.
- **Flexible Initial Sync Direction:** Choose the initial sync direction (local-to-s3, s3-to-local, or auto) based on your requirements.
- **Timestamp-Based Sync Strategy:** When set to auto, the script uses the last modified timestamps to determine the initial sync direction.
- **Deletion Handling:** Reflects file deletions in both the local folder and the S3 bucket.
- **Logging:** Detailed logs of the sync process, including any errors or important actions.

## How It Works

### Initial Sync

The initial sync direction can be set via the `--initial-sync-source` argument to either `local`, `s3`, or `auto`. If set to `auto`, the script compares the last modified timestamps of files in both locations. The direction with the most recent changes is chosen as the source for the initial sync. This ensures that the latest modifications are always prioritized during the first synchronization.

### Ongoing Sync Strategy

After the initial sync, the script regularly checks for local changes and syncs them to the S3 bucket. This approach prioritizes local modifications, reflecting any new changes or deletions in the S3 bucket.

### Deletion Handling

This script ensures that deletions in the local folder are mirrored in the S3 bucket. However, it is important to note that deletions in S3 are not mirrored locally during the continuous sync. Instead, the local file replaces the deleted one in S3 in the next sync cycle.

Consequently, if a file is deleted locally, this change will be synced to the S3 bucket, ensuring that deletions are mirrored. Conversely, if a file is deleted in S3, the local version of the file will be uploaded to S3 during the next sync, as the script starts syncing from local to S3 after the initial synchronization.

If changes in the S3 bucket are ahead of the local state, you should start the script setting the initial sync direction to `s3-to-local`.

### Logging

The script provides detailed logging for each synchronization action, including successful syncs, file changes, and any errors encountered, which is important for troubleshooting and understanding the sync behavior.

### Usage

To use this script, ensure you have Poetry and AWS CLI installed and configured with the necessary access to the S3 bucket. Modify the configuration file `config.yml` to set your local folder path, S3 bucket name, sync intervals, and other preferences.

Build the virtual environment:

```bash
poetry install
```

Run the script with Python, optionally specifying the initial sync direction:

```bash
poetry run python main.py --initial-sync-source auto
```

### Configuration

The synchronization behavior can be customized via a configuration file. This includes setting the local folder path, S3 bucket name, sync intervals, AWS profile, and other options.
