import os
from argparse import ArgumentParser, Namespace
from datetime import datetime

import requests


def request_parser(params: dict):
    print("Making request:", params)
    url = os.getenv("host_url") + "/api/v2"
    params["apikey"] = os.getenv("api_key")
    return requests.request("GET", url, params=params)


def get_libraries():
    return request_parser(
        {
            "cmd": "get_libraries",
        }
    ).json()["response"]


def get_library_section_ids():
    libraries = request_parser({"cmd": "get_libraries"}).json()["response"]
    sections = {"episode": [], "movie": [], "track": []}
    for lib in libraries["data"]:
        if lib["section_type"] == "show":
            sections["episode"].append(lib["section_id"])
        elif lib["section_type"] == "movie":
            sections["movie"].append(lib["section_id"])
        elif lib["section_type"] == "artist":
            sections["track"].append(lib["section_id"])

    return sections


def get_general_watch_history(args: Namespace):
    # Get quantity of entries to parse
    response = request_parser(
        {
            "cmd": "get_history",
            "before": str(args.year) + "-12-31",
            "after ": str(args.year) + "-01-01",
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
            "before": str(args.year) + "-12-31",
            "after ": str(args.year) + "-01-01",
            "order_column": "date",
            "order_dir": "desc",
            "start": 0,
            "length": total_length,
        }
    )

    if batch.status_code == 200:
        history = batch.json()["response"]["data"]
        cleaned = []
        for hist in history["data"]:
            if datetime.fromtimestamp(int(hist["date"])).year > args.year:
                continue
            elif datetime.fromtimestamp(int(hist["date"])).year == args.year:
                cleaned.append(hist)
            else:
                break
        history["data"] = cleaned
        return history
    else:
        return dict()


def get_user_watch_history(args: Namespace):
    # Get quantity of entries to parse
    response = request_parser(
        {
            "cmd": "get_history",
            "user": args.user,
            "before": str(args.year) + "-12-31",
            "after ": str(args.year) + "-01-01",
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
            "before": str(args.year) + "-12-31",
            "after ": str(args.year) + "-01-01",
            "order_column": "date",
            "order_dir": "desc",
            "start": 0,
            "length": total_length,
        }
    )

    if batch.status_code == 200:
        history = batch.json()["response"]["data"]
        cleaned = []
        for hist in history["data"]:
            if datetime.fromtimestamp(int(hist["date"])).year > args.year:
                continue
            elif datetime.fromtimestamp(int(hist["date"])).year == args.year:
                cleaned.append(hist)
            else:
                break
        history["data"] = cleaned
        return history
    else:
        return dict()


def get_full_media_info(section_id: str):
    full_list = []
    start = 0
    length = 25
    while True:
        response = request_parser(
            {
                "cmd": "get_library_media_info",
                "section_id": section_id,
                "start": start,
                "length": length,
            }
        )
        if response.status_code == 200:
            if len(response.json()["response"]["data"]["data"]) > 0:
                data = response.json()["response"]["data"]
                full_list.extend(data["data"])
                start += length
            else:
                break
    return full_list


def get_specific_media_info(rating_key: str):
    full_list = []
    start = 0
    length = 25
    while True:
        response = request_parser(
            {
                "cmd": "get_library_media_info",
                "rating_key": rating_key,
                "start": start,
                "length": length,
            }
        )
        if response.status_code == 200:
            if len(response.json()["response"]["data"]["data"]) > 0:
                data = response.json()["response"]["data"]
                full_list.extend(data["data"])
                start += length
            else:
                break
    return full_list


def get_episode_file_size(rating_key: int, parent_rating_key: int):
    response = request_parser(
        {
            "cmd": "get_library_media_info",
            "rating_key": parent_rating_key,
        }
    )
    if response.status_code == 200:
        season = response.json()["response"]["data"]
        for episode in season["data"]:
            if int(episode["rating_key"]) == rating_key:
                return int(episode["file_size"])

    return -1


def get_movie_file_size(section_ids: list, search_term: str):
    for section_id in section_ids:
        response = request_parser(
            {
                "cmd": "get_library_media_info",
                "section_id": section_id,
                "search": search_term,
            }
        )
        if response.status_code == 200:
            movie = response.json()["response"]
            if len(movie["data"]["data"]) > 0:
                return int(movie["data"]["data"][0]["file_size"])

    return -1
