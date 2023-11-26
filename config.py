import os

import yaml


def load_config(file_path: str) -> dict:
    """Handles loading configuration from the YAML file."""
    with open(file_path, "r") as file:
        config = yaml.safe_load(file)

    # Expand user in file paths
    config["general"]["local_folder"] = os.path.expanduser(
        config["general"]["local_folder"]
    )
    config["logging"]["log_directory"] = os.path.expanduser(
        config["logging"]["log_directory"]
    )

    return config
