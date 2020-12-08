import pydantic
import typing as t
import enum
import requests


class BoundingBox(pydantic.BaseModel):
    longitude_min: float  # "-0.292620207579333",
    latitude_min: float  # "51.4981814665016",
    longitude_max: float  #  "-0.269393792420667",
    latitude_max: float  # "51.5126385334984"


class ListingStatus(enum.Enum):
    sale = "sale"
    rent = "rent"


HTMLText = str
URL = str
ImageURL = URL


class PriceChange(pydantic.BaseModel):
    direction: str  # ""|down|up
    date: str  # "2020-08-04 09:04:48",
    percent: str  # "0%"
    price: int  # 425000


class PriceChangeSummary(pydantic.BaseModel):
    direction: str  # "down",
    percent: str  #  "-5.8%",
    last_updated_date: str  # "2020-08-28 11:31:17"


class ListedProperty(pydantic.BaseModel):
    country_code: str  #  "gb",
    num_floors: int  #  0,
    image_150_113_url: t.Optional[
        str
    ]  # "https://lid.zoocdn.com/150/113/1b47563257b8b0ad07f77e0c51e5d874bbe2a78e.jpg",
    listing_status: ListingStatus
    num_bedrooms: int  #  1,
    location_is_approximate: bool  # 0,
    image_50_38_url: t.Optional[
        str
    ]  # "https://lid.zoocdn.com/50/38/1b47563257b8b0ad07f77e0c51e5d874bbe2a78e.jpg",
    latitude: float  # 51.508545,
    furnished_state: t.Optional[str]  #  null,
    agent_address: str  # "103 Churchfield Road, Acton",
    category: str  # "Residential",
    property_type: str  #  "Flat",
    longitude: float  # -0.271638,
    thumbnail_url: str  #  "https://lid.zoocdn.com/80/60/1b47563257b8b0ad07f77e0c51e5d874bbe2a78e.jpg",
    description: str  #  ...
    post_town: t.Optional[str]  #  "London",
    details_url: str  # "https://www.zoopla.co.uk/for-sale/details/55741469?utm_source=v1:_LDITDGfCxbL9gCiebUwrTH-NwAkxrCY&utm_medium=api",
    short_description: HTMLText
    outcode: str  # "W3",
    image_645_430_url: t.Optional[
        URL
    ]  #  "https://lid.zoocdn.com/645/430/1b47563257b8b0ad07f77e0c51e5d874bbe2a78e.jpg",
    new_home: t.Optional[bool]  # "true"
    county: t.Optional[str]  #  "London",
    price: float  # "400000",
    listing_id: str  # "55741469",
    image_caption: t.Optional[str]  # "",
    image_80_60_url: t.Optional[
        str
    ]  # "https://lid.zoocdn.com/80/60/1b47563257b8b0ad07f77e0c51e5d874bbe2a78e.jpg",
    status: str  # "for_sale",
    agent_name: str  # "Aston Rowe - Acton",
    num_recepts: int  # 1,
    country: t.Optional[str]  # "England",
    first_published_date: str  # "2020-08-04 09:06:04",
    displayable_address: str  # "Horn Lane, London W3",
    floor_plan: t.Sequence[
        ImageURL
    ] = ()  # ["https://lc.zoocdn.com/2f1d7ebc813da4d65b91541e30506366fd78c1ed.jpg"]
    street_name: str  # "Horn Lane",
    num_bathrooms: int  # 1,
    agent_logo: t.Optional[
        ImageURL
    ]  # "https://st.zoocdn.com/zoopla_static_agent_logo_(635024).png",
    price_change: t.Sequence[PriceChange] = ()
    agent_phone: str  # "020 3551 9604",
    image_354_255_url: t.Optional[
        ImageURL
    ]  # "https://lid.zoocdn.com/354/255/1b47563257b8b0ad07f77e0c51e5d874bbe2a78e.jpg",
    image_url: t.Optional[
        ImageURL
    ]  #  "https://lid.zoocdn.com/354/255/1b47563257b8b0ad07f77e0c51e5d874bbe2a78e.jpg",
    last_published_date: str  # "2020-11-13 14:36:56",
    price_change_summary: t.Optional[PriceChangeSummary]


class ListingsResult(pydantic.BaseModel):
    listing: t.Sequence[ListedProperty]

    country: str  # "England",
    result_count: int  # 51,
    longitude: float  #  -0.281007,
    area_name: str  # " W3",
    street: str  # ""
    radius: float  # "0.5",
    town: str  # "",
    latitude: float  # 51.50541,
    county: str  # "London",
    bounding_box: BoundingBox
    postcode: str  # "W3 8EY"


class Client:
    def __init__(self, base_url: str, api_key: str) -> None:
        self.__base_url = base_url
        self.__api_key = api_key
        self.__session = requests.Session()

    def list_listings(
        self,
        *,
        postcode,
        radius_miles: float = None,
        maximum_price: int,
        minimum_beds: int,
        only_new_homes: bool = False,
    ) -> ListingsResult:
        # https://developer.zoopla.co.uk/docs/read/Property_listings
        params = {
            "area": postcode,
            "api_key": self.__api_key,
            "listing_status": "sale",
            "maximum_price": maximum_price,
            "minimum_beds": minimum_beds,
        }
        if only_new_homes is not None:
            # will show only new homes
            params["new_homes"] = "true"
        if radius_miles is not None:
            params["radius"] = radius_miles

        response = self.__session.get(
            f"{self.__base_url}/property_listings.json", params=params
        )
        response.raise_for_status()
        try:
            return ListingsResult.parse_obj(response.json())
        except pydantic.ValidationError:
            print(response.json())
            raise


def get_client(token=None):
    import os

    return Client(
        base_url="https://api.zoopla.co.uk/api/v1",
        api_key=token or os.environ["ZOOPLA_API_KEY"],
    )
