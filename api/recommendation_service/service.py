import json

from api.recommendation_service.models import HeroCosineModel
from constants import COURSE_SERVICE_URL
import requests


def load_heroes():
    with open('heroes.json', 'r') as file:
        heroes = json.load(file)
    return heroes
global_heroes = load_heroes()

class RecommendationService:

    def __init__(self):
        self.model = HeroCosineModel()

    def get_heroes(self, hero_ids, num_recommendations=3):
        return self.model.get_similar_heroes(hero_ids, num_recommendations)

    def get_courses(self, hero_ids, num_recommendations=5):
        similar_hero_ids = self.get_heroes(hero_ids, num_recommendations)
        courses = self.load_courses(similar_hero_ids)
        for course in courses:
            course_hero_ids = [h["id"] for h in course["heroes"]]
            selected_heroes = [hero for hero in global_heroes if hero["id"] in course_hero_ids]
            course["heroes"] = selected_heroes
        return courses

    def load_courses(self, hero_ids):
        url = COURSE_SERVICE_URL + "/api/courses/by-heroes"
        response = requests.post(url, json={"hero_ids": hero_ids})
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            return {"error": "Failed to fetch courses"}