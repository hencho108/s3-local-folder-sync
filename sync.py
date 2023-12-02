"""Contains the logic for syncing files from local to S3 and vice versa."""

import logging
import os
import subprocess
import time
from datetime import datetime, timezone

import boto3

import config

cfg = config.load_config("config.yml")
aws_profile = cfg.general.aws_profile


def get_last_modified_s3(s3_bucket_name: str) -> datetime:
    """
    Gets the last modified timestamp of the most recently updated file in an S3 bucket
    """
    s3 = boto3.client("s3")
    last_modified = None

    # List objects in the S3 bucket
    response = s3.list_objects_v2(Bucket=s3_bucket_name)
    for obj in response.get("Contents", []):
        if last_modified is None or obj["LastModified"] > last_modified:
            last_modified = obj["LastModified"]

    return last_modified


def get_last_modified_local(local_folder: str) -> datetime:
    """
    Gets the last modified timestamp of the most recently updated file in a local folder
    """
    last_modified = None

    for root, dirs, files in os.walk(local_folder):
        for name in files:
            filepath = os.path.join(root, name)
            mtime = os.path.getmtime(filepath)
            mtime_dt = datetime.fromtimestamp(mtime, timezone.utc)
            if last_modified is None or mtime_dt > last_modified:
                last_modified = mtime_dt

    return last_modified


def run_command(command: str):
    """
    Executes a shell command and return its output
    """
    try:
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        return stdout, stderr
    except Exception as e:
        logging.error(f"Error running command '{command}': {e}")
        return None, None


def sync_command(source: str, destination: str, is_source_s3: bool, delete: bool):
    """Performs a sync operation between a local folder and an S3 bucket.

    Args:
        source (str): Source path.
        destination (str): Destination path.
        is_source_s3 (bool): Flag to indicate if the source is an S3 bucket.
        delete (bool): Flag to indicate if the sync should delete files.
    """
    global aws_profile
    try:
        if is_source_s3:
            logging.info("Syncing from S3 to local")
            command = f"aws s3 sync s3://{source} {destination} --profile {aws_profile}"
        else:
            logging.info("Syncing from local to S3")
            command = f"aws s3 sync {source} s3://{destination} --profile {aws_profile}"

        if delete:
            command += " --delete"

        stdout, stderr = run_command(command)

        # Log output from aws cli
        if stdout:
            for line in stdout.decode().splitlines():
                logging.info(line.strip())

        if stderr:
            for line in stderr.decode().splitlines():
                logging.error(line.strip())

    except Exception as e:
        logging.error(f"Sync error: {e}")


def initial_sync(
    local_folder: str, s3_bucket: str, delete: bool, initial_sync_source: str = "auto"
):
    """Performs the initial sync between a local folder and an S3 bucket based on the specified direction.

    Args:
        local_folder (str): Path to the local folder.
        s3_bucket (str): Name of the S3 bucket.
        delete (bool): Flag to indicate if the sync should delete files.
        initial_sync_source (str): Direction for initial sync ('auto', 'local', or 's3').
    """
    if initial_sync_source == "auto":
        last_modified_local = get_last_modified_local(local_folder)
        last_modified_s3 = get_last_modified_s3(s3_bucket)

        if last_modified_local > last_modified_s3:
            sync_command(local_folder, s3_bucket, False, delete)
        elif last_modified_s3 > last_modified_local:
            sync_command(s3_bucket, local_folder, True, delete)

    elif initial_sync_source == "local":
        sync_command(local_folder, s3_bucket, False, delete)

    elif initial_sync_source == "s3":
        sync_command(s3_bucket, local_folder, True, delete)

    else:
        raise ValueError("Invalid initial_sync_source")


def periodic_sync(local_folder: str, s3_bucket: str, delete: bool, sync_interval: int):
    while True:
        sync_command(local_folder, s3_bucket, False, delete)
        sync_command(s3_bucket, local_folder, True, delete)
        time.sleep(sync_interval)
