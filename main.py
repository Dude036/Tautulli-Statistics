import datetime
import os.path
import re
from pprint import pprint

from dotenv import load_dotenv
import argparse
from re import findall
from statistics import add_user_stats, add_global_stats
from network import get_general_watch_history, get_user_watch_history

load_dotenv()
parser = argparse.ArgumentParser(
    prog="Tautulli Statistics Grabber",
    description="A program for retrieving and parsing watch statistics from a remote "
    "instance of Tautulli",
)
parser.add_argument(
    "-u",
    "--user",
    required=True,
    help="A string of the username you are inquiring about",
)

parser.add_argument(
    "-y",
    "--year",
    required=True,
    type=int,
    help="The calender year to extract data from",
)

args = parser.parse_args()


def export_to_html(watch_history: dict):
    # Read in the file
    with open("template.html", "r") as file:
        filedata = file.read()

    # Replace strings
    replacements = findall(r"({% ([\w\d_]+) %})", filedata)
    print("============ Replacing Data ============")
    for point in replacements:
        print("Replacing " + point[0])
        try:
            filedata = re.sub(point[0], str(watch_history[point[1]]), filedata)
        except KeyError as e:
            print("Key missing:", point[1])
            print(e)
        except Exception as e:
            print("Unknown error:", point[1])
            print(e)

    # Write the file out again
    with open(args.user + "-output.html", "w") as file:
        file.write(filedata)


if __name__ == "__main__":
    # Process all user data
    start = datetime.datetime.now()
    general_data = {"user_name": args.user}
    all_data = get_general_watch_history(args)
    general_data.update(add_global_stats(all_data, args))

    # Process specific user data
    user_data = get_user_watch_history(args)
    general_data.update(add_user_stats(user_data, general_data, args))

    # Add potential note based on the Username

    if os.path.isfile(args.user + ".note.txt"):
        with open(args.user + ".note.txt", "r") as personal_note:
            general_data.update({"personal_note": ''.join(personal_note.readlines())})
    else:
        general_data.update({"personal_note": ""})

    # Export
    end = datetime.datetime.now()

    print("============ Collection Time ===========")
    print(end - start)
    print("============ Collected Data ============")
    pprint(general_data)

    export_to_html(general_data)
