"""Contains the logic for syncing files from local to S3 and vice versa."""

import logging
import subprocess


def run_command(command):
    try:
        process = subprocess.Popen(
            command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate()

        return stdout, stderr
    except Exception as e:
        logging.error(f"Error running command '{command}': {e}")
        return None, None


def sync_files(source: str, destination: str, delete: bool = True):
    # TODO: don't sync while sync is in progress
    try:
        command = f"aws s3 sync {source} {destination}"

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
        logging.error(f"Error syncing from {source} to {destination}: {e}")
