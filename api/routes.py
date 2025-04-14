from . import common_bp
from flask import jsonify, request

@common_bp.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({"message": "Hello from Flask API"})

