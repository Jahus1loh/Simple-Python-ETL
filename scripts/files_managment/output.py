import logging
import logging.config
import shutil
from pathlib import Path

import tomllib

logging.config.fileConfig("config\\logging.conf")
logger = logging.getLogger()

with Path("config\\config.toml").open("rb") as f:
    cfg = tomllib.load(f)
    dir_path = cfg["output"]["path"]


def create_output_directory() -> None:
    """Function to create an empty output directory
    and any missing parent directories
    """
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def delete_output_directory() -> None:
    """Function to delete an output directory

    Args:
        file_path (str): Path to directory to delete
    """
    path = Path(dir_path)
    try:
        shutil.rmtree(path)
    except FileNotFoundError as e:
        logger.exception(e)
