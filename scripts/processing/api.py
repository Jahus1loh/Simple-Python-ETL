import json
import logging
import logging.config
from http import HTTPStatus
from pathlib import Path

import backoff
import requests
import tomllib
from scripts.structures.data_types import ProductData

with Path("config\\config.toml").open("rb") as f:
    cfg = tomllib.load(f)
    retry_status_codes = {
        HTTPStatus[name].value for name in cfg["request"]["retry_codes"]
    }
    base_url = cfg["api"]["base_url"]
    basket_endpoint_url = cfg["api"]["endpoints"]["basket"]
    user_endpoint_url = cfg["api"]["endpoints"]["users"]
    product_endpoint_url = cfg["api"]["endpoints"]["products"]
    product_selected_fields = cfg["api"]["returned_fields"]["products"]
    user_selected_fields = cfg["api"]["returned_fields"]["users"]


logging.config.fileConfig("config\\logging.conf")
logger = logging.getLogger()


def get_users_url(pagination: int, skip: int) -> str:
    """Function to create a url for users endpoint for dummyjson API

    Args:
        pagination (int): Number of retrieved products in single call
        skip (int): Number of skiped results

    Returns:
        _type_: Returns a url for users endpoint
    """
    limit = f"limit={pagination}"
    skip_str = f"skip={skip}"
    select = f"select={user_selected_fields}"
    url = f"{base_url}{user_endpoint_url}?{limit}&{skip_str}&{select}"
    return url


def get_products_url(pagination: int, skip: int) -> str:
    """Function to create a url for products endpoint for dummyjson API

    Args:
        pagination (int): Number of retrieved products in single call
        skip (int): Number of skiped results

    Returns:
        str: Returns a url for products endpoint
    """
    limit = f"?limit={pagination}"
    skip_str = f"&skip={skip}"
    select = f"&select={product_selected_fields}"
    url = f"{base_url}{product_endpoint_url}?{limit}&{skip_str}&{select}"

    return url


def get_basket_url(user_id: int) -> str:
    """Function to create a url for users basket endpoint for dummyjson API

    Args:
        user_id (int): ID of a user that the basket data is retrieved for

    Returns:
        _type_: Returns a url for users basket endpoint
    """
    url = f"{base_url}{basket_endpoint_url}{str(user_id)}"
    return url


def clean_product_api_response(response: requests.Response | None) -> bool:
    """Function to check if the product API response can be proccessed or
    there are some errors with the response

    Args:
        response (requests.Response | None): Response to check

    Returns:
        bool: Returns boolean indicating if the response is ready for
        processing
    """
    if (
        response
        and response.status_code == HTTPStatus.OK
        and response.json()["products"] != []
    ):
        return True
    return False


@backoff.on_predicate(
    backoff.runtime,
    predicate=lambda r: r.status_code is not None
    and r.status_code in retry_status_codes,
    value=lambda r: int(r.headers.get("Retry-After")),
    jitter=None,
)
def get_products_batch(pagination: int, skip: int) -> requests.Response | None:
    """Function to get a batch of users data from dummyjson API with
    exponential backoff when 429 error arises

    Args:
        pagination (int): Number of users to retrieve
        skip (int): Number of users to skip while searching
    """
    url = get_products_url(pagination, skip)
    try:
        response = requests.get(url)
    except Exception as e:
        logger.exception(e)
    else:
        return response
    return None


def get_all_products(pagination: int = 10, skip: int = 0) -> None:
    """Function to get all users data from dummyjson API

    Args:
        pagination (int, optional): Number of users to retrieve
        in one API call. Defaults to 10.
    """
    all_products: list[ProductData] = []
    while response := get_products_batch(pagination, skip):
        if clean_product_api_response(response):
            skip += pagination
            response_json = response.json()
            all_products = all_products + response_json.get("products", [])
        else:
            break

    with Path("output\\product_data.json").open("w") as f:
        json.dump(all_products, f, ensure_ascii=False, indent=4)
    logger.info("Data about all products was retrieved and saved to json file")


@backoff.on_predicate(
    backoff.runtime,
    predicate=lambda r: r.status_code is not None
    and r.status_code in retry_status_codes,
    value=lambda r: int(r.headers.get("Retry-After")),
    jitter=None,
)
def get_users_batch(pagination: int, skip: int) -> requests.Response | None:
    """Function to get a batch of users data from dummyjson API with
    exponential backoff when 429 error arises

    Args:
        pagination (int): Number of users to retrieve
        skip (int): Number of users to skip while searching
    """
    url = get_users_url(pagination, skip)
    try:
        response = requests.get(url)
    except Exception as e:
        logger.exception(e)
    else:
        return response
    return None


@backoff.on_predicate(
    backoff.runtime,
    predicate=lambda r: r.status_code is not None
    and r.status_code in retry_status_codes,
    value=lambda r: int(r.headers.get("Retry-After")),
    jitter=None,
)
def get_user_basket(user_id: int) -> requests.Response | None:
    """Function to get a users basket data from dummyjson API with
    exponential backoff when 429 error arises

    Args:
        user_id (int): ID of searched user
    """
    url = get_basket_url(user_id)
    try:
        response = requests.get(url)
        return response
    except Exception as e:
        logger.exception(e)
    return None
