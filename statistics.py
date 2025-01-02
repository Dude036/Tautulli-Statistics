from network import *
from datetime import datetime

month_translator = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December"
}


def prettify_time(time: int):
    date = datetime.fromtimestamp(time)
    origin = datetime.fromtimestamp(0)
    td = date - origin
    ret_str = str(td.days) + " days "
    ret_str += str(td.seconds // 60 // 60) + " hrs "
    ret_str += str(td.seconds % 60) + " mins"
    return ret_str


def add_user_stats(user_history: dict, total_collection: dict, args: Namespace):
    collected_stats = {
        "user_watch_time_minutes": stat_total_watch_time(user_history),
        "user_tv_watch_time_minutes": stat_media_watch_time(user_history, 'episode'),
        "user_movie_watch_time_minutes": stat_media_watch_time(user_history, 'movie'),
        "user_music_watch_time_minutes": stat_media_watch_time(user_history, 'track'),
    }

    ## Derived stats
    collected_stats["user_watch_time"] = prettify_time(collected_stats['user_watch_time_minutes'])
    collected_stats["user_tv_watch_time"] = prettify_time(collected_stats['user_tv_watch_time_minutes'])
    collected_stats["user_movie_watch_time"] = prettify_time(collected_stats['user_movie_watch_time_minutes'])
    collected_stats["user_music_watch_time"] = prettify_time(collected_stats['user_music_watch_time_minutes'])

    ## Special stats
    # Top Show by count
    tv_popular_show_count = stat_tv_popular_show_count(user_history)
    top_ten = sorted(
        tv_popular_show_count.keys(),
        key=lambda x: tv_popular_show_count[x],
        reverse=True,
    )[:10]

    for i in range(10):
        if i >= len(top_ten):
            collected_stats["user_top_tv_show_count_" + str(i + 1) + "_name"] = "---"
            collected_stats["user_top_tv_show_count_" + str(i + 1) + "_count"] = "---"
        else:
            collected_stats["user_top_tv_show_count_" + str(i + 1) + "_name"] = top_ten[i]
            collected_stats["user_top_tv_show_count_" + str(i + 1) + "_count"] = (
                tv_popular_show_count[top_ten[i]]
            )


    # Bandwidth Info
    collected_stats["user_bandwidth_used"], platform_bandwidth = stat_bandwidth_used(
        user_history
    )

    # Translate from byte to gigabyte
    collected_stats["user_bandwidth_used"] = round(
        collected_stats["user_bandwidth_used"] / 1024 / 1024 / 1024, 2
    )
    collected_stats["user_tv_bandwidth_used"] = round(
        platform_bandwidth["episode"] / 1024 / 1024 / 1024, 2
    )
    collected_stats["user_movie_bandwidth_used"] = round(
        platform_bandwidth["movie"] / 1024 / 1024 / 1024, 2
    )
    collected_stats["user_music_bandwidth_used"] = round(
        platform_bandwidth["track"] / 1024 / 1024 / 1024, 2
    )
    collected_stats["user_bandwidth_used_percentage"] = round(
        100
        * collected_stats["user_bandwidth_used"]
        / total_collection["total_bandwidth_used"],
        3,
    )

    # Time data
    date_data = stat_times_of_day(user_history, args.year)
    for hour in range(24):
        collected_stats['user_hour_' + '{:02d}'.format(hour) + '_watch_label'] = '{:02d}'.format(hour) + ':00'
        collected_stats['user_hour_' + '{:02d}'.format(hour) + '_watch_count'] = date_data[hour]

    for month in range(1, 13):
        collected_stats['user_' + month_translator[month] + '_watch_count'] = date_data[month_translator[month]]


    return collected_stats


def add_global_stats(history: dict, args: Namespace):
    ## Direct Stats
    collected_stats = {
        "total_watch_time_minutes": stat_total_watch_time(history),
        "total_tv_watch_time_minutes": stat_media_watch_time(history, 'episode'),
        "total_movie_watch_time_minutes": stat_media_watch_time(history, 'movie'),
        "total_music_watch_time_minutes": stat_media_watch_time(history, 'track'),
    }

    ## Derived stats
    collected_stats["total_watch_time"] = prettify_time(collected_stats["total_watch_time_minutes"])
    collected_stats["total_tv_watch_time"] = prettify_time(collected_stats["total_tv_watch_time_minutes"])
    collected_stats["total_movie_watch_time"] = prettify_time(collected_stats["total_movie_watch_time_minutes"])
    collected_stats["total_music_watch_time"] = prettify_time(collected_stats["total_music_watch_time_minutes"])

    collected_stats["total_active_use_time"] = round(collected_stats["total_watch_time_minutes"] / (60 * 24 * 365), 2)

    ## Special Platform Stats
    # Top show by Count
    tv_popular_show_count = stat_tv_popular_show_count(history)
    top_ten = sorted(
        tv_popular_show_count.keys(),
        key=lambda x: tv_popular_show_count[x],
        reverse=True,
    )[:10]

    for i in range(10):
        if i >= len(top_ten):
            collected_stats["total_top_tv_show_count_" + str(i + 1) + "_name"] = "---"
            collected_stats["total_top_tv_show_count_" + str(i + 1) + "_count"] = "---"
        else:
            collected_stats["total_top_tv_show_count_" + str(i + 1) + "_name"] = top_ten[i]
            collected_stats["total_top_tv_show_count_" + str(i + 1) + "_count"] = tv_popular_show_count[top_ten[i]]

    # Most popular Platform
    platform_info = stat_platform_counter(history)
    top_platform = sorted(platform_info.keys(), key=lambda x: platform_info[x], reverse=True)[:10]

    for i in range(10):
        if i >= len(top_platform):
            collected_stats["total_top_platform_count_" + str(i + 1) + "_name"] = "---"
            collected_stats["total_top_platform_count_" + str(i + 1) + "_count"] = "0"
        else:
            collected_stats["total_top_platform_count_" + str(i + 1) + "_name"] = top_platform[i]
            collected_stats["total_top_platform_count_" + str(i + 1) + "_count"] = platform_info[top_platform[i]]


    # Media added this year counters
    tv_shows_added = stat_get_recently_added("episode", args.year)
    collected_stats["total_tv_show_added_count"] = tv_shows_added['show_counter']
    collected_stats["total_tv_episode_added_count"] = tv_shows_added['episode_counter']
    collected_stats["total_tv_added_list"] = tv_shows_added['show_list']

    collected_stats["total_movies_added_count"] = stat_get_recently_added("movie", args.year)['movie_counter']

    music_added = stat_get_recently_added("track", args.year)
    collected_stats["total_music_album_added_count"] = music_added['album_counter']
    collected_stats["total_music_track_added_count"] = music_added['track_counter']

    # Total Bandwidth used
    collected_stats["total_bandwidth_used"], platform_bandwidth = stat_bandwidth_used(
        history
    )

    # Translate from byte to gigabyte
    collected_stats["total_bandwidth_used"] = round(
        collected_stats["total_bandwidth_used"] / 1024 / 1024 / 1024, 2
    )
    collected_stats["total_tv_bandwidth_used"] = round(
        platform_bandwidth["episode"] / 1024 / 1024 / 1024, 2
    )
    collected_stats["total_movie_bandwidth_used"] = round(
        platform_bandwidth["movie"] / 1024 / 1024 / 1024, 2
    )
    collected_stats["total_music_bandwidth_used"] = round(
        platform_bandwidth["track"] / 1024 / 1024 / 1024, 2
    )

    collected_stats["total_tv_bandwidth_used_percent"] = round(
        100
        * collected_stats["total_tv_bandwidth_used"]
        / collected_stats["total_bandwidth_used"],
        3,
    )
    collected_stats["total_movie_bandwidth_used_percent"] = round(
        100
        * collected_stats["total_movie_bandwidth_used"]
        / collected_stats["total_bandwidth_used"],
        3,
    )
    collected_stats["total_music_bandwidth_used_percent"] = round(
        100
        * collected_stats["total_music_bandwidth_used"]
        / collected_stats["total_bandwidth_used"],
        3,
    )

    # Time data
    date_data = stat_times_of_day(history, args.year)
    for hour in range(24):
        collected_stats['total_hour_' + '{:02d}'.format(hour) + '_watch_label'] = '{:02d}'.format(hour) + ':00'
        collected_stats['total_hour_' + '{:02d}'.format(hour) + '_watch_count'] = date_data[hour]

    for month in range(1, 13):
        collected_stats['total_' + month_translator[month] + '_watch_count'] = date_data[month_translator[month]]

    return collected_stats


def stat_total_watch_time(history: dict):
    """
    Returns the total watch time in minutes.

    :param history: dictionary of total user interactions from ``network.get_general_watch_history()`` or ``network.get_user_watch_history()``
    :return: total watch time in minutes
    :rtype: int
    """
    minutes = 0
    for entry in history["data"]:
        minutes += entry["play_duration"]
    return minutes

def stat_times_of_day(history: dict, year: int):
    # Month Data
    date_data = {
        'January': 0,
        'February': 0,
        'March': 0,
        'April': 0,
        'May': 0,
        'June': 0,
        'July': 0,
        'August': 0,
        'September': 0,
        'October': 0,
        'November': 0,
        'December': 0,
    }

    # Hour of the Day Data
    for hour in range(24):
        date_data[hour] = 0

    for entry in history["data"]:
        specific = datetime.fromtimestamp(entry['date'])
        if specific.year == year:
            date_data[month_translator[specific.month]] += 1
            date_data[specific.hour] += 1

    return date_data


def stat_media_watch_time(history: dict, media_type: str):
    """
    Returns the total watch time in minutes by media type.
    :param history:  dictionary of total user interactions from ``network.get_general_watch_history()`` or ``network.get_user_watch_history()``
    :param media_type: The Media type to narrow search. Accepts: ('episode', 'movie', 'track')
    :return: an integer of minutes of watch time
    """
    minutes = 0
    for entry in history["data"]:
        if "media_type" in entry and entry["media_type"] == media_type:
            minutes += entry["play_duration"]
    return minutes


def stat_tv_popular_show_count(history: dict):
    show_counter = {}
    for entry in history["data"]:
        if "media_type" in entry and entry["media_type"] == "episode":
            # Add episode to show watch counter
            if entry["grandparent_title"] not in show_counter:
                show_counter[entry["grandparent_title"]] = 0
            show_counter[entry["grandparent_title"]] += 1
    return show_counter


def stat_tv_popular_show_duration(history: dict):
    show_counter = {}
    for entry in history["data"]:
        if "media_type" in entry and entry["media_type"] == "episode":
            # Add episode to show watch counter
            if entry["grandparent_title"] not in show_counter:
                show_counter[entry["grandparent_title"]] = 0
            show_counter[entry["grandparent_title"]] += entry["play_duration"]
    return show_counter


def stat_platform_counter(history: dict):
    platform_counter = {}
    for entry in history["data"]:
        if "media_type" in entry and entry["media_type"] == "episode":
            if entry["platform"] not in platform_counter:
                platform_counter[entry["platform"]] = 0
            platform_counter[entry["platform"]] += 1
    return platform_counter


def stat_bandwidth_used(history: dict):
    bandwidth = 0
    platform_bandwidth = {"episode": 0, "movie": 0, "track": 0}

    sections = get_library_section_ids()

    for entry in history["data"]:
        size = 0
        if entry["media_type"] == "episode":
            size = get_episode_file_size(
                entry["rating_key"], entry["parent_rating_key"]
            )

        elif entry["media_type"] == "track":
            size = get_episode_file_size(
                entry["rating_key"], entry["parent_rating_key"]
            )

        elif entry["media_type"] == "movie":
            size = get_movie_file_size(sections["movie"], entry["title"])

        # Add to bandwidth if valid size
        if size > 0:
            bandwidth += size
            platform_bandwidth[entry["media_type"]] += size

    return bandwidth, platform_bandwidth


def stat_get_recently_added(library: str, year: int):
    sections = get_library_section_ids()
    recently_added = {}

    if library == "episode":
        show_counter = 0
        episode_counter = 0
        show_list = set()
        for section in sections["episode"]:
            for show in get_full_media_info(section):
                for season in get_specific_media_info(show['rating_key']):
                    if datetime.fromtimestamp(int(season["added_at"])).year == year:
                        if show['title'] not in show_list:
                            show_list.add(show["title"])
                            show_counter += 1

                    for episode in get_specific_media_info(season['rating_key']):
                        if datetime.fromtimestamp(int(episode["added_at"])).year != year:
                            continue
                        else:
                            episode_counter += 1

        recently_added['show_counter'] = show_counter
        recently_added['episode_counter'] = episode_counter
        recently_added['show_list'] = show_list

    elif library == "movie":
        movie_counter = 0
        for section in sections["movie"]:
            for movie in get_full_media_info(section):
                if datetime.fromtimestamp(int(movie["added_at"])).year != year:
                    continue
                else:
                    movie_counter += 1

        recently_added['movie_counter'] = movie_counter

    elif library == "track":
        album_counter = 0
        track_counter = 0
        album_list = set()

        for section in sections["episode"]:
            for artist in get_full_media_info(section):
                for album in get_specific_media_info(artist['rating_key']):
                    if datetime.fromtimestamp(int(album["added_at"])).year == year:
                        if album['title'] not in album_list:
                            album_list.add(album["title"])
                            album_counter += 1

                    for track in get_specific_media_info(album['rating_key']):
                        if datetime.fromtimestamp(int(track["added_at"])).year != year:
                            continue
                        else:
                            track_counter += 1

        recently_added['album_counter'] = album_counter
        recently_added['track_counter'] = track_counter
        recently_added['album_list'] = album_list

    return recently_added
