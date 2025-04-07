from flask import Flask
from config import DevelopmentConfig, ProductionConfig
from api.models import db
from api import api_blueprint
import os

def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Khởi tạo SQLAlchemy với app
    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(api_blueprint, url_prefix='/api')
    return app

if __name__ == '__main__':
    # Chọn cấu hình dựa trên biến môi trường FLASK_ENV
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        config_class = ProductionConfig
    else:
        config_class = DevelopmentConfig

    app = create_app(config_class)
    app.run()
