from . import api_blueprint
from flask import jsonify, request

@api_blueprint.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({"message": "Hello from Flask API"})

