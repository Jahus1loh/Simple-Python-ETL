import json
from collections.abc import Sequence
from http import HTTPStatus
from pathlib import Path

import requests
from scripts.files_managment.csv import write_user_data_to_csv_file
from scripts.processing.api import get_user_basket
from scripts.processing.user import User
from scripts.structures.data_types import ProductData, UserData


def check_if_all_users_were_retrieved(
        response: requests.Response, skip: float
) -> bool:
    """Function to check if all users were retrieved from the API by comparing
    the number of skipped users to the total number of users

    Args:
        response (requests.Response): The user endpoint API call response
        skip (float): Number of users that were skipped in the API call

    Returns:
        bool: Returns True if all users were retrieved and False if there are
        some users left to retrieve
    """
    return skip > get_total_users(response)


def clean_user_api_response(response: requests.Response) -> bool:
    """Function to check if the user API response meets conditions for
    further processing such as being not None, having HTTTP Status equal
    to OK and list of users not being empty

    Args:
        response (requests.Response | None): The user endpoint API call
        response or None

    Returns:
        bool: Returns True if the response can be processed and False if
        it can't
    """
    if (
        response.status_code == HTTPStatus.OK
        and response.json()["users"] != []
    ):
        return True
    return False


def get_users_batch_from_api_response(
    response: requests.Response,
) -> Sequence[UserData]:
    """Function to retrieve users batch from the API response

    Args:
        response (requests.Response): The user endpoint API call response

    Returns:
        Sequence[UserData]: Returns the sequence of dictionaries with user data
    """
    users_batch: Sequence[UserData] = response.json()["users"]
    return users_batch


def get_total_users(response: requests.Response) -> float:
    """Function to get total number of users that should be retrieved by API

    Args:
        response (requests.Response): Response of users endpoint call

    Returns:
        float: Returns the total number of users or -1 if the total is not
        available
    """
    total_users: float = response.json().get("total", -1)
    return total_users


def load_all_products() -> Sequence[ProductData]:
    """Function to load all products data from product data json

    Returns:
        Sequence[ProductData]: Returns sequence of dictionaries containing
        product data
    """
    all_products: Sequence[ProductData]
    with Path("output\\product_data.json").open("r") as f:
        all_products = json.load(f)
    return all_products


def process_user_data_batch(
    user_data_batch: Sequence[UserData], all_products: Sequence[ProductData]
) -> Sequence[UserData]:
    """Function to process batch of user data

    Args:
        user_data_batch (Sequence[UserData]): Batch of user data
        all_products (Sequence[ProductData]): Sequence of dictionaries
        containing all product data

    Returns:
        Sequence[UserData]: Returns sequence of processed dictionaries
        with user data
    """
    processed_user_data_batch: list[UserData] = []
    for user_dict in user_data_batch:
        user = User(user_dict, all_products)
        user_basket = get_user_basket(user.id)

        if isinstance(user_basket, requests.Response):
            user.get_most_frequent_item_in_baskets(user_basket.json())

        # wersja 1
        user.get_country_name_based_on_coordinates()
        write_user_data_to_csv_file(user.as_dict())

        # wersja 2
        # user.process_user_data_and_prepare_for_saving(user_basket)
        user_dict = user.as_dict()
        processed_user_data_batch.append(user_dict)

    return processed_user_data_batch


def prepare_user_data_for_db_insertion(
    user_data_batch: Sequence[UserData],
) -> Sequence[tuple[object, ...]]:
    """Function to prepare the user data to be in format required to insert
    the data into db

    Args:
        user_data_batch (Sequence[UserData]): Sequence of dictionaries
        containing user data

    Returns:
        Sequence[tuple[object, ...]]: Returns sequence of tuples containing
        values of user data dictionary
    """
    to_db = [(tuple(user_data.values())) for user_data in user_data_batch]
    return to_db
