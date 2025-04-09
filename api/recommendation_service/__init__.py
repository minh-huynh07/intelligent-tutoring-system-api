from flask import Blueprint

# Tạo blueprint với tên là "api"
recommendation_bp = Blueprint('recommendation_service', __name__)

# Import các route để đăng ký vào blueprint
from . import routes  # Khi import, các route trong routes.py sẽ được đăng ký vào api_blueprint
