import typing as t
from pathlib import Path
import csv
import argparse
from pymongo import MongoClient
import sys


class SchoolsStorage:
    def __init__(self, mongodb_client: MongoClient) -> None:
        self._collection = mongodb_client.db["schools"]

    def add_school_from_dict(self, school_details: t.Mapping):
        school_details["_id"] = school_details["urn"]
        self._collection.insert_one(school_details)


def init_schools_collection(csv_path):
    """Initialize database.

    Download schools information from https://www.compare-school-performance.service.gov.uk/download-data

    The archive contains file named 'england_school_information.csv' that is used to
    initialize schools collection in the MongoDB.
    """
    storage = SchoolsStorage(
        mongodb_client=MongoClient("mongodb://root:rootpaswd@localhost:27017")
    )
    for data in csv.DictReader(
        Path(csv_path).read_text(encoding="utf-8-sig").splitlines()
    ):
        # all the keys in the dict are uppercase, it's not great
        storage.add_school_from_dict(_convert_keys_to_lowercase(data))


def _convert_keys_to_lowercase(data):
    return {k.lower(): v for k, v in data.items()}


def cli(argv: t.Sequence[str]):
    ...


def parse_args(argv):
    parser = argparse.ArgumentParser()
    initdb_parser = parser.add_subparsers(title="initdb")
    return parser.parse_args(argv)


if __name__ == "__main__":
    cli(sys.argv)
