def add_stat(d: dict, k: str, v):
    d[k] = v
    return d


def add_all_stats(history: dict, prefix: str = ''):
    collected_stats = {
        prefix + 'total_watch_time': stat_total_watch_time(history),
        prefix + 'total_tv_watch_time': stat_tv_watch_time(history),
        prefix + 'total_movie_watch_time': stat_movie_watch_time(history),
        prefix + 'total_music_watch_time': stat_music_listen_time(history),
        prefix + 'stat_tv_popular_show_count': stat_tv_popular_show_count(history),
        prefix + 'stat_tv_popular_show_duration': stat_tv_popular_show_duration(history),
        prefix + 'stat_platform_counter': stat_platform_counter(history)
    }

    return collected_stats


def stat_total_watch_time(history: dict):
    return history.get("total_duration")


def stat_tv_watch_time(history: dict):
    minutes = 0
    for entry in history['data']:
        if 'media_type' in entry and entry['media_type'] == 'episode':
            minutes += entry['play_duration']
    return minutes


def stat_movie_watch_time(history: dict):
    minutes = 0
    for entry in history['data']:
        if 'media_type' in entry and entry['media_type'] == 'movie':
            minutes += entry['play_duration']
    return minutes


def stat_music_listen_time(history: dict):
    minutes = 0
    for entry in history['data']:
        if 'media_type' in entry and entry['media_type'] == 'track':
            minutes += entry['play_duration']
    return minutes


def stat_tv_popular_show_count(history: dict):
    show_counter = {}
    for entry in history['data']:
        if 'media_type' in entry and entry['media_type'] == 'episode':
            # Add episode to show watch counter
            if entry['grandparent_title'] not in show_counter:
                show_counter[entry['grandparent_title']] = 0
            show_counter[entry['grandparent_title']] += 1
    return show_counter

def stat_tv_popular_show_duration(history: dict):
    show_counter = {}
    for entry in history['data']:
        if 'media_type' in entry and entry['media_type'] == 'episode':
            # Add episode to show watch counter
            if entry['grandparent_title'] not in show_counter:
                show_counter[entry['grandparent_title']] = 0
            show_counter[entry['grandparent_title']] += entry['play_duration']
    return show_counter


def stat_platform_counter(history: dict):
    platform_counter = {}
    for entry in history['data']:
        if 'media_type' in entry and entry['media_type'] == 'episode':
            if entry['platform'] not in platform_counter:
                platform_counter[entry['platform']] = 0
            platform_counter[entry['platform']] += 1
    return platform_counter

