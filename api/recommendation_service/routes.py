from numbers import Number
from typing import List

from . import recommendation_bp
from flask import jsonify, request

from .service import RecommendationService

@recommendation_bp.route('/heroes', methods=['POST'])
def get_heroes():
    data = request.get_json()
    hero_ids: List[Number] = data.get("heroIds", [])

    if not hero_ids or len(hero_ids) == 0:
        return jsonify({"error": "Invalid input"}), 400

    service = RecommendationService()
    results = service.get_heroes(hero_ids)

    return jsonify({"results": results})

@recommendation_bp.route('/courses', methods=['POST'])
def get_courses():
    data = request.get_json()
    hero_ids: List[Number] = data.get("heroIds", [])

    if not hero_ids or len(hero_ids) == 0:
        return jsonify({"error": "Invalid input"}), 400

    service = RecommendationService()
    results = service.get_courses(hero_ids)
    return jsonify({"results": results})
