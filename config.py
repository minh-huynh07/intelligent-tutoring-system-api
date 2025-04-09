import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 5000
    # Sử dụng biến môi trường DATABASE_URL_DEV nếu có, nếu không sẽ sử dụng chuỗi mặc định (ví dụ với SQLite)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'mysql+pymysql://app:iamapp@db:3306/intelligent_tutoring_system')

class ProductionConfig(Config):
    DEBUG = False
    # Sử dụng biến môi trường DATABASE_URL_PROD, ví dụ kết nối MySQL trên production
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        'mysql+pymysql://app:iamapp@db:3306/intelligent_tutoring_system'
    )
