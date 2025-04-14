from . import recommendation_bp
from flask import jsonify, request

@recommendation_bp.route('/get-heroes', methods=['GET'])
def test_endpoint():
    return jsonify({"message": "Hello from Flask API"})

