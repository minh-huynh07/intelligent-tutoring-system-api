import pandas as pd
from utils import create_folder, save_file, get_data
from constants import DOTA2_URL, HEROES_URL, HEROES_STATS_URL, BENCHMARK_BY_HERO_ID_URL
from bs4 import BeautifulSoup
import re

class HeroCrawler:

    def __init__(self):
        self.base_url = DOTA2_URL
        self.heroes = []

    def get_html(self, url):
        text = get_data(url, response_type="html")
        return BeautifulSoup(text, "html.parser")

    def get_all_heroes(self):
        soup = self.get_html(self.base_url + "/wiki/Heroes")
        hero_grid = soup.select("#content table tr td a[title]")
        heroes = []

        for hero_anchor in hero_grid:
            name = hero_anchor["title"].strip()
            if name:
                url = hero_anchor["href"]
                heroes.append({
                    "name": name,
                    "url": url
                })
        return heroes

    def normalize_text(self, text):
        text = text.lower()
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def get_hero(self, hero):
        soup = self.get_html(self.base_url + hero["url"])
        abilities_info = soup.find_all("div", class_="ability-background")

        results = []
        for info in abilities_info:
            parent = info.parent
            results.append(self.normalize_text(parent.text))

        return " ".join(results)

    def save_to_file(self, filename, content, folder="heroes_data"):
        create_folder(folder)
        save_file(f'{folder}/{filename}', content)

    def save_to_csv(self, folder="heroes_data", filename="heroes_ability.csv"):
        create_folder(folder)
        df = pd.DataFrame(self.heroes)
        df.to_csv(f"{folder}/{filename}", index=False)

    def start(self):
        self.heroes = self.get_all_heroes()
        for hero in self.heroes:
            # if hero["name"] != "Alchemist":
            #     continue
            print(f"Fetching data for {hero['name']}...")

            abilities = self.get_hero(hero)
            self.save_to_file(f"{hero["name"]}.txt", abilities)
            hero["ability"] = abilities

        print(f"Total heroes found: {len(self.heroes)}")
        self.save_to_csv()

class HeroStatsCrawler:
    def __init__(self):
        self.heroes = []
        self.hero_stats = []

    def get_percentile(self, arr, percentile):
        expected_percentile = next(filter(lambda x: x["percentile"] == percentile, arr), None)
        return expected_percentile["value"] if expected_percentile else ""

    def calculate_benchmark(self, benchmark):
        return {
            "gold_per_min": self.get_percentile(benchmark["gold_per_min"], 0.5),
            "xp_per_min": self.get_percentile(benchmark["xp_per_min"], 0.5),
            "kills_per_min": self.get_percentile(benchmark["kills_per_min"], 0.5),
            "last_hits_per_min": self.get_percentile(benchmark["last_hits_per_min"], 0.5),
            "hero_damage_per_min": self.get_percentile(benchmark["hero_damage_per_min"], 0.5),
            "hero_healing_per_min": self.get_percentile(benchmark["hero_healing_per_min"], 0.5),
            "tower_damage": self.get_percentile(benchmark["tower_damage"], 0.5),
        }

    def fetch_hero_stats(self):
        self.hero_stats = get_data(HEROES_STATS_URL)
        for stat in self.hero_stats:
            for key, value in stat.items():
                if isinstance(value, list):
                    stat[key] = ",".join(map(str, value))

    def save_to_csv(self, folder="heroes_stats_data", filename="heroes_stats.csv"):
        create_folder(folder)
        df = pd.DataFrame(self.hero_stats)
        df.to_csv(f"{folder}/{filename}", index=False)

    def start(self):
        self.heroes = get_data(HEROES_URL)
        self.fetch_hero_stats()

        for hero in self.heroes:
            hero_id = hero["id"]
            hero_name = hero["localized_name"]
            print(f"Fetching data for {hero_name}...")

            benchmark_data = get_data(f"{BENCHMARK_BY_HERO_ID_URL}?hero_id={hero_id}")
            if not benchmark_data:
                break

            hero_benchmark = self.calculate_benchmark(benchmark_data["result"])
            hero_stat = next(filter(lambda x: x["id"] == hero_id, self.hero_stats), None)
            if hero_stat:
                hero_stat.update(hero_benchmark)

        self.save_to_csv()
#
heroes_crawler = HeroCrawler()
heroes_crawler.start()
#
# hero_stats_crawler = HeroStatsCrawler()
# hero_stats_crawler.start()