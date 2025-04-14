import requests
import pandas as pd
import json
import time

from utils import create_folder

HEROES_URL = "https://api.opendota.com/api/heroes"
BENCHMARK_BY_HERO_ID_URL = "https://api.opendota.com/api/benchmarks" # ?hero_id=1
HEROES_STATS_URL = "https://api.opendota.com/api/heroStats"

def get_json(url):
    response = requests.get(url)

    retry_count = 0
    while response.status_code == 429 and retry_count < 5:
        time.sleep(60)
        retry_count += 1
        response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        return None


def get_percentile(arr, percentile):
    expected_percentile = next(filter(lambda x: x["percentile"] == percentile, arr), None)
    return expected_percentile["value"] if expected_percentile else ""

def calculate_benchmark(benchmark):
    return {
        "gold_per_min": get_percentile(benchmark["gold_per_min"], 0.5),
        "xp_per_min": get_percentile(benchmark["xp_per_min"], 0.5),
        "kills_per_min": get_percentile(benchmark["kills_per_min"], 0.5),
        "last_hits_per_min": get_percentile(benchmark["last_hits_per_min"], 0.5),
        "hero_damage_per_min": get_percentile(benchmark["hero_damage_per_min"], 0.5),
        "hero_healing_per_min": get_percentile(benchmark["hero_healing_per_min"], 0.5),
        "tower_damage": get_percentile(benchmark["tower_damage"], 0.5),
    }

def get_hero_stats():
    arr = get_json(HEROES_STATS_URL)
    for stat in arr:
        for key, value in stat.items():
            if isinstance(value, list):
                stat[key] = ",".join(map(str, value))
    return arr

heros = get_json(HEROES_URL)
heroes_stats = get_hero_stats()

for hero in heros:

    hero_id = hero["id"]
    hero_name = hero["localized_name"]
    print(f"Fetching data for {hero_name}...")

    benchmark_data = get_json(f"{BENCHMARK_BY_HERO_ID_URL}?hero_id={hero_id}")
    if not benchmark_data:
        break
    hero_benchmark = calculate_benchmark(benchmark_data["result"])

    hero_stat = next(filter(lambda x: x["id"] == hero_id, heroes_stats), None)
    if hero_stat:
        hero_stat.update(hero_benchmark)

create_folder("stats")
df = pd.DataFrame(heroes_stats)
df.to_csv("stats/heroes_stats.csv", index=False)

