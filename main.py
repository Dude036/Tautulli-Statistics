import os
from dotenv import load_dotenv
import argparse
import requests
from re import findall
from statistics import add_all_stats
from datetime import datetime

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
    "-u", "--user", required=True, help="A string of the username you are inquiring about"
)

parser.add_argument(
    "-y", "--year", required=True, help="The calender year to extract data from"
)
args = parser.parse_args()


def request_parser(params: dict):
    url = os.getenv("host_url") + "/api/v2"
    params["apikey"] = os.getenv("api_key")
    return requests.request("GET", url, params=params)


def get_recently_added_tv():
    # Setup batch retrieval
    start = 0
    recent = set()
    while True:
        response = request_parser(
            {
                "cmd": "get_recently_added",
                "count": "10",
                "start": str(start),
                "media_type": 'episode',
            }
        )
        if response.status_code == 200:
            data = response.json()["response"]['recently_added']
            for added in data:
                date = datetime.fromtimestamp(added['added_at'])
                if date.year == args.year:
                    recent.add(added['grandparent_title'] + ' Season ' + added['parent_media_index'])




def get_general_watch_history():
    # Get quantity of entries to parse
    response = request_parser(
        {
            "cmd": "get_history",
            "before": args.year + "-12-31",
            "after ": args.year + "-01-01",
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
            "before": args.year + "-12-31",
            "after ": args.year + "-01-01",
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


def get_user_watch_history():
    # Get quantity of entries to parse
    response = request_parser(
        {
            "cmd": "get_history",
            "user": args.user,
            "before": args.year + "-12-31",
            "after ": args.year + "-01-01",
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
            "user": args.user,
            "before": args.year + "-12-31",
            "after ": args.year + "-01-01",
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
    replacements = findall(r"({% ([\w_]+) %})", filedata)
    for point in replacements:
        if args.verbose:
            print("Replacing " + point[0])
        filedata = filedata.replace(point[0], watch_history[point[1]])

    # Write the file out again
    with open("output.html", "w") as file:
        file.write(filedata)


if __name__ == "__main__":
    # Process all user data
    general_data = {'user_name': args.user}
    all_data = get_general_watch_history()
    general_data.update(add_all_stats(all_data, 'all_'))

    # Process specific user data
    user_data = get_user_watch_history()

    # Export

    export_to_html(general_data)
