import requests

from typing import cast

from scripts.database.db_connection import (
    insert_user_data_into_table,
    recreate_db
)
from scripts.files_managment.output import (
    create_output_directory,
    delete_output_directory,
)
from scripts.processing.api import (
    get_all_products,
    get_users_batch
)
from scripts.processing.processing import (
    check_if_all_users_were_retrieved,
    clean_user_api_response,
    get_users_batch_from_api_response,
    load_all_products,
    process_user_data_batch,
    prepare_user_data_for_db_insertion,
)


def main() -> None:
    pagination = 30
    skip = 0
    delete_output_directory()
    create_output_directory()

    recreate_db()

    get_all_products(pagination=pagination)
    all_products = load_all_products()

    while True:
        response = get_users_batch(pagination, skip)
        if response and clean_user_api_response(response):
            skip += pagination
            users_batch = get_users_batch_from_api_response(response)
            processed_users_batch = process_user_data_batch(
                users_batch, all_products
            )
            user_data_to_insert = prepare_user_data_for_db_insertion(
                processed_users_batch
            )
            insert_user_data_into_table(user_data_to_insert)
            if check_if_all_users_were_retrieved(response, skip):
                break
        else:
            break


if __name__ == "__main__":
    main()
