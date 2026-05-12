import logging
import logging.config
from collections.abc import MutableMapping, Sequence
from typing import cast

from geopy.geocoders import Nominatim
from scripts.files_managment.csv import write_user_data_to_csv_file
from scripts.structures.data_types import (
    AddressData, BasketData, ProductData, UserData
)

logging.config.fileConfig("config\\logging.conf")
logger = logging.getLogger()


class User:
    id: int
    firstName: str
    lastName: str
    age: int
    gender: str
    height: float
    weight: float
    address: AddressData
    latitude: float
    longitude: float
    country: str | None
    top_product_category_in_basket: str | None
    geolocator: Nominatim

    def __init__(
        self, dictionary: UserData, all_products: Sequence[ProductData]
    ) -> None:
        """Initialization method for user class

        Args:
            dictionary (UserData): User data saved in dictionary
        """
        for k, v in dictionary.items():
            setattr(self, k, v)
        coordinates = self.address.get("coordinates", None)
        if coordinates:
            lat = coordinates.get("lat", None)
            lon = coordinates.get("lng", None)
            if lat and lon:
                self.latitude = lat
                self.longitude = lon
        self.country = None
        self.top_product_category_in_basket = None
        self.all_prodcuts = all_products

    def get_country_name_based_on_coordinates(self) -> None:
        """Function to get the country name from the user's address
        coordinates using geopy.geocoders.Nominatim and its reverse method
        """
        country_name: str | None = None
        geolocator = Nominatim(user_agent="task_2")
        query: str = f"{self.latitude}, {self.longitude}"

        try:
            location = geolocator.reverse(
                query=query,
                language="en",
                exactly_one=True,
            )
        except Exception as e:
            logger.exception(e)
        else:
            if location:
                country_name = location.raw["address"]["country"]

        self.country = country_name

    def process_user_data_and_prepare_for_saving(
            self, basket: BasketData
    ) -> None:
        """Function to process gathered user data by finding the country name
        based on coordinates and finding most frequent item in user baskets
        and prepare it for saving in the csv and db
        """
        self.get_country_name_based_on_coordinates()
        self.get_most_frequent_item_in_baskets(basket)
        write_user_data_to_csv_file(self.as_dict())

    def get_most_frequent_item_in_baskets(
            self, user_basket: BasketData
    ) -> None:
        """Function to get the most frequent category of items from the
        gathered user's basket data

        Returns:
            _type_: Returns None if basket for searched user was not found
            or the basket was found but user's cart was empty
        """
        bought_categories_freq: MutableMapping[str, int] = {}
        if not user_basket:
            return None

        carts_list = user_basket.get("carts", [])
        if carts_list == []:
            return None

        for cart in carts_list:
            products = cart.get("products", [])
            bought_categories_freq = self.count_category_frequencies(
                products, bought_categories_freq
            )

        self.get_most_frequent_product(bought_categories_freq)

    def count_category_frequencies(
        self,
        products: Sequence[ProductData],
        bought_categories_freq: MutableMapping[str, int] = {},
    ) -> MutableMapping[str, int]:
        """Function to count the frequencies of each product category

        Args:
            products (Sequence[ProductData]): Sequence of all products data
            with id, name and category specified for each product
            bought_categories_freq (MutableMapping[str, int], optional):
            _description_. Defaults to {}.

        Returns:
            MutableMapping[str, int]: Returns frequency of each product
            category
        """
        for product in products:
            product = self.match_product_to_category(product)
            product_quantity = product.get("quantity", 0)
            product_category = product.get("category", "")
            if product_category in bought_categories_freq.keys():
                bought_categories_freq[product_category] += product_quantity
            else:
                bought_categories_freq[product_category] = product_quantity
        return bought_categories_freq

    def match_product_to_category(self, product: ProductData) -> ProductData:
        """Function to match the product to its category

        Args:
            product (ProductData): Dictionary of searched product data with
            its name and id

        Returns:
            ProductData: Returns the dictionary with product data with its
            name, category and id
        """
        product_id = product.get("id", -1)
        if product_id != -1:
            searched_product = self.all_prodcuts[product_id - 1]
            products_category = searched_product["category"]
            product["category"] = products_category

        return product

    def get_most_frequent_product(
        self, bought_products_freq: MutableMapping[str, int]
    ) -> None:
        """Function to get the most frequent product category from the
        product category frequency

        Args:
            bought_products_freq (MutableMapping[str, int]): Frequency of
            product categories put in the basket
        """
        bought_products_freq_sorted = sorted(
            bought_products_freq.items(), key=lambda x: x[1], reverse=True
        )

        self.top_product_category_in_basket = bought_products_freq_sorted[0][0]

    def as_dict(self) -> UserData:
        attributes_to_skip = ["all_prodcuts", "address"]
        dict_keys = self.__dict__.keys()
        pr = {
            key: None for key in dict_keys if key not in attributes_to_skip
        }
        for key, value in self.__dict__.items():
            if key in attributes_to_skip:
                continue
            pr[key] = value
        user_data_as_dict = cast(UserData, pr)
        return user_data_as_dict
