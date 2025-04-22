from flask import Flask

from api.steam_service import steam_bp
from config import DevelopmentConfig, ProductionConfig  # Ensure proper imports here
from api import common_bp
from api.recommendation_service import recommendation_bp
from api.models import db
import os
import socket
import time


def wait_for_mysql(host, port, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=2):
                print("MySQL is available!")
                return True
        except Exception:
            print("Waiting for MySQL to be ready...")
            time.sleep(2)
    raise Exception("Timed out waiting for MySQL.")


def create_app(config_class):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize DB if using SQLAlchemy
    db.init_app(app)

    with app.app_context():
        db.create_all()

    # Register blueprint for common services
    # app.register_blueprint(common_bp, url_prefix='/api')
    app.register_blueprint(recommendation_bp, url_prefix='/api/recommendation')
    app.register_blueprint(steam_bp, url_prefix='/auth')

    return app


if __name__ == '__main__':
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'production':
        config_class = ProductionConfig
    else:
        config_class = DevelopmentConfig

    # Get debug setting from the configuration (or you can also use os.environ FLASK_DEBUG)
    debug = config_class.DEBUG

    # **Wait for MySQL before creating the app**
    if debug:
        wait_for_mysql("db", 3306)

    # Now create the app after ensuring the database is ready
    app = create_app(config_class)

    host = app.config.get('HOST', '0.0.0.0')
    port = app.config.get('PORT', 5000)

    app.run(host=host, port=port, debug=debug)