import argparse
import csv
import sys
import typing as t
from pathlib import Path


import tqdm
from pymongo import MongoClient
import pymongo.errors


class SchoolsStorage:
    def __init__(self, mongodb_client: MongoClient) -> None:
        self._collection = mongodb_client.db["schools"]

    def add_school_from_dict(self, school_details: t.Mapping):
        school_details["_id"] = school_details["urn"]
        self._collection.insert_one(school_details)


def init_schools_collection(args):
    """Initialize database.

    Download schools information from https://www.compare-school-performance.service.gov.uk/download-data

    The archive contains file named 'england_school_information.csv' that is used to
    initialize schools collection in the MongoDB.
    """
    csv_path = args.school_info_csv
    storage = SchoolsStorage(
        mongodb_client=MongoClient("mongodb://root:rootpaswd@localhost:27017")
    )

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

    args = parser.parse_args(argv)
    if args.func:
        args.func(args)


if __name__ == "__main__":
    parse_args(sys.argv[1:])
