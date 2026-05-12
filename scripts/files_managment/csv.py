import logging
import logging.config
from pathlib import Path

import tomllib
from scripts.structures.data_types import UserData
from scripts.structures.decorators import run_once

logging.config.fileConfig("config\\logging.conf")
logger = logging.getLogger()

with Path("config\\config.toml").open("rb") as f:
    cfg = tomllib.load(f)
    file_path = cfg["csv"]["path"]


@run_once
def create_new_file_with_headers(user_data: UserData) -> None:
    """Function to create a file with csv headers

    Args:
        file_path (str): Path to file to create
        headers (str): String of headers of csv columns
    """
    headers = ",".join(list(user_data.keys())) + "\n"
    with Path(file_path).open("w") as f:
        f.write(headers)
        logger.info(f"{file_path} file was created with headers")


def write_user_data_to_csv_file(user_data: UserData) -> None:
    """Function to write user data into csv file

    Args:
        user_data (UserData): Dictionary of user data
    """
    create_new_file_with_headers(user_data)
    values = ",".join(map(str, list(user_data.values()))) + "\n"
    with Path(file_path).open("a") as f:
        f.write(values)
