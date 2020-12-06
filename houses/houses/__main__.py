import argparse
import csv
import sys
import typing as t
from pathlib import Path


import tqdm
from pymongo import MongoClient
import pymongo.errors


class SchoolsStorage:
    """Example of entry in the storage.

        {
            "urn": "100285",
            "laname": "Hackney",
            "la": "204",
            "estab": "4714",
            "laestab": "2044714",
            "schname": "Cardinal Pole Catholic School",
            "street": "205 Morning Lane",
            "locality": "Hackney",
            "address3": "",
            "town": "London",
            "postcode": "E9 6LG",
            "schstatus": "Open",
            "opendate": "",
            "closedate": "",
            "minorgroup": "Maintained school",
            "schooltype": "Voluntary aided school",
            "isprimary": "0",
            "issecondary": "1",
            "ispost16": "1",
            "agelow": "11",
            "agehigh": "19",
            "gender": "Mixed",
            "relchar": "Roman Catholic",
            "admpol": "Non-selective"
        }

    """

    def __init__(self, mongodb_client: MongoClient) -> None:
        self._collection = mongodb_client.db["schools"]

    def update_each_school(self, update_fn):
        for idx, school in enumerate(self._collection.find(), start=1):
            updated = update_fn(idx, school)
            if updated is not None:
                self._collection.update_one({"_id": school["_id"]}, {"$set": updated})

    def add_school_from_dict(self, school_details: t.Mapping):
        school_details["_id"] = school_details["urn"]
        self._collection.insert_one(school_details)

    def iter_schools(
        self,
        towns=None,
        ignore_girls_school=False,
        postcode_areas=None,
        agehigh=None,
        boroughs=None,
    ):
        and_operands = [
            {"schstatus": "Open"},
            {"issecondary": "1"},
            {"gender": {"$ne": "Boys"}},
            {"location": {"$exists": True}},
        ]
        if ignore_girls_school:
            and_operands.append({"gender": {"$ne": "Girls"}})
        if towns:
            and_operands.append({"town": {"$in": towns}})
        if postcode_areas:
            and_operands.append({"location.postcode_area": {"$in": postcode_areas}})
        if agehigh:
            and_operands.append({"agehigh": str(agehigh)})
        if boroughs:
            and_operands.append({"laname": {"$in": boroughs}})

        yield from (
            {
                "urn": record["urn"],
                "postcode": record["postcode"],
                "town": record["town"],
                "locality": record["locality"],
                "laname": record["laname"],
                "schooltype": record["schooltype"],
                "minorgroup": record["minorgroup"],
                "latitude": record["location"]["latitude"],
                "longitude": record["location"]["longitude"],
                "schname": record["schname"],
                "agehigh": record["agehigh"],
                "agelow": record["agelow"],
            }
            for record in self._collection.find({"$and": and_operands})
        )

    def iter_school_urn_to_coordinates(self, town=None):
        yield from (
            {
                "urn": record["urn"],
                "latitude": record["location"]["latitude"],
                "longitude": record["location"]["longitude"],
            }
            for record in self._collection.find(
                {
                    "$and": [
                        {"town": town},
                        {"issecondary": "1"},
                        {"gender": {"$ne": "Boys"}},
                    ]
                }
            )
            # for record in self._collection.find({"location": {"$exists": True}})
        )

    def iter_schools_by_urn(self, urns):
        yield from (
            record for record in self._collection.find({"urn": {"$in": list(urns)}})
        )

    def iter_all_post_codes(self):
        for entry in self._collection.find():
            postcode = entry.get("postcode")
            if postcode:
                yield postcode

    @classmethod
    def init(cls):
        return cls(
            mongodb_client=MongoClient("mongodb://root:rootpaswd@localhost:27017")
        )


def collect_all_postcodes(args):
    """Collect all postcodes from the mongodb."""
    import requests

    session = requests.Session()

    def update_coordinates_by_postcode(idx, school_dict):
        postcode = school_dict.get("postcode")
        if not postcode or school_dict.get(
            "location"
        ):  # or (school_dict.get("longitude") and school_dict.get("latitude")):
            return None

        response = session.get("http://api.getthedata.com/postcode/" + postcode)
        # example of response
        # {'status': 'match', 'match_type': 'unit_postcode', 'input': 'BN25 2JB', 'data': {'postcode': 'BN25 2JB', 'status': 'live', 'usertype': 'large', 'easting': 548577, 'northing': 100718, 'positional_quality_indicator': 1, 'country': 'England', 'latitude': '50.786996', 'longitude': '0.106457', 'postcode_no_space': 'BN252JB', 'postcode_fixed_width_seven': 'BN252JB', 'postcode_fixed_width_eight': 'BN25 2JB', 'postcode_area': 'BN', 'postcode_district': 'BN25', 'postcode_sector': 'BN25 2', 'outcode': 'BN25', 'incode': '2JB'}, 'copyright': ['Contains OS data (c) Crown copyright and database right 2020', 'Contains Royal Mail data (c) Royal Mail copyright and database right 2020', 'Contains National Statistics data (c) Crown copyright and database right 2020']}
        response.raise_for_status()
        print(idx, end=" ", flush=True)
        return dict(location=response.json()["data"])

    SchoolsStorage.init().update_each_school(update_coordinates_by_postcode)
    # Path("postcodes.txt").write_text("\n".join(storage.iter_all_post_codes()))


def init_schools_collection(args):
    """Initialize database.

    Download schools information from https://www.compare-school-performance.service.gov.uk/download-data

    The archive contains file named 'england_school_information.csv' that is used to
    initialize schools collection in the MongoDB.
    """
    csv_path = args.school_info_csv
    storage = SchoolsStorage.init()

    lines = Path(csv_path).read_text(encoding="utf-8-sig").splitlines()
    reader = csv.DictReader(lines)
    for data in tqdm.tqdm(reader, total=len(lines)):
        # all the keys in the dict are uppercase, it's not great
        try:
            storage.add_school_from_dict(_convert_keys_to_lowercase(data))
        except pymongo.errors.DuplicateKeyError:
            pass


def _convert_keys_to_lowercase(data):
    return {k.lower(): v for k, v in data.items()}


def cli(argv: t.Sequence[str]):
    ...
    # {$and: [{ schstatus: "Open" }, { issecondary: "1" }, {$or: [{gender: "Mixed"}, {gender: "Girls"}]}]}


def parse_args(argv):
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(title="start")
    initdb_parser = subparsers.add_parser("initdb")

    initdb_parser.add_argument(
        "school_info_csv", default="./data/england_school_information.csv"
    )
    initdb_parser.set_defaults(func=init_schools_collection)

    collect_post_codes = subparsers.add_parser("collectpostcodes")
    collect_post_codes.set_defaults(func=collect_all_postcodes)

    args = parser.parse_args(argv)
    if args.func:
        args.func(args)


if __name__ == "__main__":
    parse_args(sys.argv[1:])
