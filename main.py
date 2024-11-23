import simplejson as json
import os
from dotenv import load_dotenv
import argparse
import requests
from pprint import pprint

load_dotenv()
parser = argparse.ArgumentParser(
    prog="Tautulli Statistics Grabber",
    description="A program for retrieving and parsing watch statistics from a remote "
    "instance of Tautulli",
)
parser.add_argument(
    "-v",
    "--verbose",
    action=argparse.BooleanOptionalAction,
    help="Enables verbose logging of program running",
)
parser.add_argument(
    "-u", "--user", help="A string of the username you are inquiring about"
)


def request_parser(params: dict):
    url = os.getenv("host_url") + "/api/v2"
    params["apikey"] = os.getenv("api_key")
    return requests.request("GET", url, params=params)


def get_user_watch_history(username: str):
    # Get quantity of entries to parse
    response = request_parser(
        {
            "cmd": "get_history",
            "user": username,
            "before": "2024-12-31",
            "after ": "2024-01-01",
            "order_column": "date",
            "order_dir": "desc",
            "start": 0,
            "length": 1,
        }
    )
    total_length = 0
    if response.status_code == 200:
        data = response.json()["response"]["data"]
        total_length = data["recordsFiltered"]

    batch = request_parser(
        {
            "cmd": "get_history",
            "user": username,
            "before": "2024-12-31",
            "after ": "2024-01-01",
            "order_column": "date",
            "order_dir": "desc",
            "start": 0,
            "length": total_length,
        }
    )
    if batch.status_code == 200:
        return batch.json()["response"]["data"]
    else:
        return dict()


def export_to_html(watch_history: dict):
    # Read in the file
    with open("template.html", "r") as file:
        filedata = file.read()

    # Replace strings
    filedata = filedata.replace(
        "{% total_watch_time %}", watch_history["total_duration"]
    )

    # Write the file out again
    with open("output.html", "w") as file:
        file.write(filedata)


if __name__ == "__main__":
    args = parser.parse_args()
    user_data = get_user_watch_history("Dude036")
    export_to_html(user_data)
