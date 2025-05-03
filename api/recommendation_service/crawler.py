import os
import pandas as pd
from utils import create_folder, save_file, get_data
from constants import DOTA2_URL, HEROES_URL, HEROES_STATS_URL, BENCHMARK_BY_HERO_ID_URL
from bs4 import BeautifulSoup
import re

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

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
        ability = self.get_hero_ability(soup)
        recommended_items = self.get_recommend_item(soup)
        return ability, recommended_items

    def get_hero_ability(self, soup):
        abilities_info = soup.find_all("div", class_="ability-background")

        results = []
        for info in abilities_info:
            parent = info.parent
            results.append(self.normalize_text(parent.text))

        return " ".join(results)

    def get_recommend_item(self, soup):
        h2_recommended_items = soup.find("span", id="Recommended_Items").parent

        recommended_items = []
        next_element = h2_recommended_items.find_next_sibling("ul")
        while next_element and next_element.name != 'h2':
            if next_element.name == "ul":
                item_links = next_element.select(".image-link > a[title]")
                for link in item_links:
                    recommended_items.append(self.normalize_text(link.text))
            next_element = next_element.find_next_sibling()

        return ",".join(recommended_items)

    def save_to_file(self, filename, content, folder="heroes_data"):
        create_folder(folder)
        save_file(os.path.join(BASE_DIR, folder, filename), content)

    def save_to_csv(self, folder="heroes_data", filename="heroes_data.csv"):
        create_folder(folder)
        df = pd.DataFrame(self.heroes)
        df.to_csv(os.path.join(BASE_DIR, folder, filename), index=False)

    def start(self):
        self.heroes = self.get_all_heroes()
        for hero in self.heroes:
            # if hero["name"] != "Alchemist":
            #     continue
            print(f"Fetching data for {hero['name']}...")

            abilities, recommended_items = self.get_hero(hero)
            self.save_to_file(f"{hero["name"]}.txt", abilities, "heroes_data/ability")
            self.save_to_file(f"{hero["name"]}.txt", recommended_items, "heroes_data/recommended_items")
            hero["ability"] = abilities
            hero["recommended_items"] = recommended_items

        print(f"Total heroes found: {len(self.heroes)}")
        self.save_to_csv()

class HeroStatsCrawler:
    def __init__(self):
        self.heroes = []
        self.hero_stats = []

    def get_percentile(self, arr, percentiles: []):
        for percentile in percentiles:
            expected_percentile = next(filter(lambda x: x["percentile"] == percentile, arr), None)
            if expected_percentile and expected_percentile["value"] != 0:
                return expected_percentile["value"]
        return 0

    def calculate_benchmark(self, benchmark):
        return {
            "gold_per_min": self.get_percentile(benchmark["gold_per_min"], [0.5]),
            "xp_per_min": self.get_percentile(benchmark["xp_per_min"], [0.5]),
            "kills_per_min": self.get_percentile(benchmark["kills_per_min"], [0.5]),
            "last_hits_per_min": self.get_percentile(benchmark["last_hits_per_min"], [0.5]),
            "hero_damage_per_min": self.get_percentile(benchmark["hero_damage_per_min"], [0.5]),
            "hero_healing_per_min": self.get_percentile(benchmark["hero_healing_per_min"], [0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99]),
            "tower_damage": self.get_percentile(benchmark["tower_damage"], [0.5]),
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
        df.to_csv(os.path.join(BASE_DIR, folder, filename), index=False)

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
# heroes_crawler = HeroCrawler()
# heroes_crawler.start()
#
# hero_stats_crawler = HeroStatsCrawler()
# hero_stats_crawler.start()
#
# df = pd.read_csv("heroes_stats_data/heroes_stats.csv")
# df["img"] = df["img"].apply(lambda x: CLOUDFLARE_OPEN_DOTA_URL + x)
# cols = ["id", "localized_name", "img"]
# heroes = df[cols]
# heroes.rename(columns={"localized_name": "name"}, inplace=True)
# heroes.to_json("heroes_stats_data/heroes.json", orient="records", indent=4)