from collections.abc import Mapping, Sequence
from typing import TypedDict


class AddressData(TypedDict):
    address: str
    city: str
    state: str
    stateCode: str
    postalCode: str
    coordinates: Mapping[str, float]
    country: str


class UserData(TypedDict):
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


class ProductData(TypedDict):
    id: int
    title: str
    category: str
    price: float
    quantity: int
    total: float
    discountPercentage: float
    discountedTotal: float
    thumbnail: str


class CartData(TypedDict):
    id: int
    products: Sequence[ProductData]


class BasketData(TypedDict):
    carts: Sequence[CartData]
    total: int
    skip: int
    limit: int
