import requests

HEROES_URL = "https://api.opendota.com/api/heroes"
BENCHMARK_BY_HERO_ID_URL = "https://api.opendota.com/api/benchmarks" # ?hero_id=1
HEROES_STATS_URL = "https://api.opendota.com/api/heroStats"

def get_json(url):
    response = requests.get(url)

    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Failed to fetch data. HTTP Status Code: {response.status_code}")

def calculate_benchmark(benchmark):
    # Calculate the benchmark based on the provided data
    # This is a placeholder function. You can implement your own logic here.
    return {
        "hero_id": benchmark["hero_id"],
        "games_played": benchmark["games_played"],
        "win_rate": benchmark["win_rate"],
        "kda": benchmark["kda"],
        "gold_per_minute": benchmark["gold_per_minute"],
        "xp_per_minute": benchmark["xp_per_minute"]
    }

data = []

heros = get_json(HEROES_URL)
heroes_stats = get_json(HEROES_STATS_URL)

for hero in heros:
    hero_id = hero["id"]
    hero_name = hero["localized_name"]
    print(f"Fetching data for {hero_name}...")
    hero_stats = get_json(f"{BENCHMARK_BY_HERO_ID_URL}?hero_id={hero_id}")
    heroes_stats.append(hero_stats)
    print(f"Data for {hero_name} saved.")
